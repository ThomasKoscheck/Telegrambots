#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chatterbot import ChatBot
import telepot
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import logging
import time
import codecs
import sys
import re
import os
import random

#own sripts (must be in the same folder)
import imagescraper     #returns photos
import giphy    #returns gif's
import translate    #translates into german
import video  #returns videos
import faceanalyze  #return face details
           
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None) #utf8mb4 activate

#path and name of the disclaimer 
disclaimer = 'disclaimer.txt'

#path and name of the errorlog
errorfile = 'error.log'

#insert valid database URI here
db_uri="mongodb://your_mongodatabase_uri_here"

#insert database name here
db_name="your_mongodatabase_name_here"

#used for special actions
Zeige = ['zeige', 'zeig', 'schicke', 'schick','sende', 'schreibe', 'schreib']
Bilder = ['bilder','bild', 'foto', 'photo']
Gif = ['gif', 'gifs']
Translate = ['\xc3\x9cbersetze', 'bedeutet', 'heißt']
Video = ['video', 'videos', 'clip', 'clips', 'film', 'filme', 'youtubevideo', 'youtubevideos']

#remove markup
removemarkup = ReplyKeyboardRemove()

# Uncomment the following line to enable verbose logging
# logging.basicConfig(level=logging.INFO)

#create a new instance of a ChatBot
susan = ChatBot("Susan", 
			  storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
			  
			  logic_adapters=[
                                "chatterbot.logic.MathematicalEvaluation", 
							    #"chatterbot.logic.TimeLogicAdapter",
							  { 
							  'import_path': 'chatterbot.logic.BestMatch'
							  }
							  ],	
			  filters=["chatterbot.filters.RepetitiveResponseFilter"],			  
			  database_uri=db_uri,
			  database=db_name,
			  trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
			  )

susan.train("chatterbot.corpus.german")

#checks if user is already registered
def userCheck(chat_id):
	#path and name of the disclaimer
	datafile = file('disclaimer.txt')	

	found = False
	for line in datafile:
		if str(chat_id) in line:
			found = True
	return found

	
#finding a word in a string	
def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

#function to save log messages to specified log file/print it to terminal
def log(message, path, terminal = False):
	# open the specified log file
	file = open(path,"a")
	# write log message with timestamp to log file
	file.write(message)
	# close log file
	file.close
		
	#output in terminal (for debugging)
	if terminal == True:
		print str(message)

#finding and returning Pronomen 
def findePronomen(input):
	if findWholeWord('einem')(input.lower()):  #checks for 'Zeige mir Bilder von einem Hund'		
		index = input.find('einem') + 6
		return index, 'von einem '		

	elif findWholeWord('einer')(input.lower()): #"checks for 'Bilder von einer Katze'
		index = input.find('einer') + 6
		return index, 'von einer '

	elif findWholeWord('von')(input.lower()):   #"checks for 'Bilder von Katzen'									 
		index = input.find('von') + 4
		return index, 'von '
								

	elif findWholeWord('vom')(input.lower()):   #checks for 'Bilder vom Matterhorn' 									 
		index = input.find('vom') + 4
		return index, 'vom '
	
#Main loop
class ChatHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatHandler, self).__init__(*args, **kwargs)

    #finding actionword
    def findActionWord(self, input, username):
        count = 0

        while count < len(Zeige):
            if Zeige[count] in str(input.lower()): #checks if input contains any words from Zeige[]

				#sending images			
                count2 = 0													
                while count2 < len(Bilder):				
                    if Bilder[count2] in str(input.lower()): #checks if input contains any words from Bilder[]
					    #sending this because downloading and sending the image takes a moment
                        self.sender.sendMessage(str("Einen Moment, ich suche das beste Bild für dich heraus... ⏱"))

                        index, pronomen = findePronomen(input)							
                        imagescraper.search((input[index:]).encode('utf-8'), chat_id)    #calling imagescraper.py

                        success = sendFoto('jpg')
                        if success == True:		#images was sent successful
                            self.sender.sendMessage(str("So, hier ein Bild " + pronomen + "'" + input[index:].encode('utf-8') + "'"))	
                        return True																										
                    
                    count2 += 1

				#sending gifs
                count2 = 0
                while count2 < len(Gif):
                    if Gif[count2] in str(input.lower()): #checks if input contains any words from Gif[]

                        index, pronomen = findePronomen(input)

                        giphy.downloadGif(input[index:].encode('utf-8'), chat_id)
                        success = sendFoto('gif')
                        if success == True:		#gif was sent successful
                            self.sender.sendMessage(str("Hier, ein GIF " + pronomen + "'" + input[index:].encode('utf-8') + "'"))
                        return True			

                    count2 += 1	

				#sending videos
                count2 = 0
                while count2 < len(Gif):
                    if Video[count2] in str(input.lower()): #checks if input contains any words from Videos[]

                        index, pronomen = findePronomen(input)
                        result = video.fetch_youtube_url(input[index:].encode('utf-8')) #hands over the searchterm to video.py, getting link to video back

                        self.sender.sendMessage(result, str("Hier, ein Video mit den Stichworten " + "'" +  input[index:].encode('utf-8') + "'"))					
                        return True			

                count2 += 1	   																											
            count = count + 1																												

        count = 0
        count2 = 0

		#translating
        if Translate[0] in str(input.lower()): #checks if input contains any words from Translate[]					
            index = input.find('\xc3\x9cbersetze') + 11			
            translation = translate.translate(input[index:].encode('utf-8'))	
            if translation == input[index:].encode('utf-8'): #translation was from german to german -> no translation needed
                return False
            else:				
                self.sender.sendMessage(str("'" + input[index:].encode('utf-8') + "' bedeutet: " + translation))
                return True	

        if Translate[1] in str(input.lower()):  #checks if input contains any words from Translate[]								
            index = input.find('bedeutet') + 9						
            translation = translate.translate(input[index:].encode('utf-8'))					
            if translation == input[index:].encode('utf-8'): #translation was from german to german -> no translation needed
                return False
            else:				
                self.sender.sendMessage(str("'" + input[index:].encode('utf-8') + "' bedeutet: " + translation))	
                return True		

        return False

	#sending images and deleting the folder afterwards
    def sendFoto(self, filetype):
        if filetype == 'gif':
            try:
                self.sender.sendDocument(open('tmp/'  + str(chat_id) + '/image.gif'))
                os.system('rm -r tmp/' + str(chat_id))	
                return True

            except:        
                self.sender.sendMessage('Hmm, da habe ich nichts gefunden. Zum Trost ein Bild von einer Katze.')
                self.sender.sendPhoto(open('tmp/katze.jpg'))
                return False	#error sending a gif

        else:
            try:
                self.sender.sendPhoto(open('tmp/'  + str(chat_id) + '/image.' + str(filetype)))
                os.system('rm -r tmp/' + str(chat_id))	
                return True

            except:        
                self.sender.sendMessage('Hmm, da habe ich nichts gefunden. Zum Trost ein Bild von einer Katze.')
                self.sender.sendPhoto(open('tmp/katze.jpg'))
                return False	#error sending an image

	#any input from telepot.DelegatorBot comes here
    def on_chat_message(self, msg):
        global chat_id
        content_type, chat_type, chat_id = telepot.glance(msg)
        reload(sys)
        sys.setdefaultencoding("utf-8")

        try:			
            chat_id = msg['chat']['id']
            firstname = msg['from']['first_name'].encode('utf8')
            #group_name = msg['chat']['title']        
            #str(content_type)

            try: 
                username = msg['from']['username'].encode('utf8')

            except:  
                #falls user keinen usernamen besitzt
                username = firstname       

            if content_type == 'photo':
                try:
                    bot.download_file(msg['photo'][-1]['file_id'], 'tmp/%s.jpg' % chat_id)
                    imagepath = 'tmp/' + str(chat_id) + '.jpg'

                    #aufruf und übergabe zu gesichtsanalyse
                    details = faceanalyze.getdetails(chat_id, imagepath)
               
                    #Auswertung der Analyse
                    ##gender = str(details['faces'][0]['attributes']['gender']['value']) #Male, Female
                    ##age =  str(details['faces'][0]['attributes']['age']['value'])
                    ##ethnie = str(details['faces'][0]['attributes']['ethnicity']['value']) #White, Black, Asian  

                    glass = str(details['faces'][0]['attributes']['glass']['value']) #None, Normal, Dark
                    facequality = str(details['faces'][0]['attributes']['facequality']['value']) #>70.1              
                    smile = details['faces'][0]['attributes']['smile']['value'] #threshold 30.1
                           
                    #Emotionen
                    neutral = str(details['faces'][0]['attributes']['emotion']['neutral'])
                    sadness = str(details['faces'][0]['attributes']['emotion']['sadness'])
                    disgust = str(details['faces'][0]['attributes']['emotion']['disgust'])
                    anger = str(details['faces'][0]['attributes']['emotion']['anger'])
                    surprise = str(details['faces'][0]['attributes']['emotion']['surprise'])
                    fear = str(details['faces'][0]['attributes']['emotion']['fear'])
                    happiness = str(details['faces'][0]['attributes']['emotion']['happiness'])

                    #Fügt alle Emotionen in eine Liste und sortiert absteigend -> Erste Emotion ist am wahrscheinlichsten
                    emotions =[neutral, sadness, disgust, anger, surprise, fear, happiness]
                    emotions.sort(reverse=True)

                    #finde die Emotion
                    if emotions[0] == neutral:
                        semotion = "Neutral"
                    elif  emotions[0] == sadness:
                        semotion = "Traurig"
                    elif  emotions[0] == disgust:
                        semotion = "Empört"
                    elif  emotions[0] == anger:
                        semotion = "wütend"
                    elif  emotions[0] == surprise:
                        semotion = "überrascht"
                    elif  emotions[0] == fear:
                        semotion = "ängstlich"
                    elif  emotions[0] == happiness:
                        semotion = "glücklich"

                    #übersetze Brillen 
                    if glass == "None":
                        sglass = "Keine Brille"
                    elif glass == "Normal":
                        sglass = "Normale Brille"
                    elif glass == "Dark":
                        sglass = "Sonnenbrille"
                
                    self.sender.sendMessage(str("Die Analyse hat folgendes ergeben: 📄\n\n" +
                                            "Geschlecht: " + str(translate.translate(str(details['faces'][0]['attributes']['gender']['value']).encode('utf-8'))) + '\n' +
                                            "Alter: " + str(details['faces'][0]['attributes']['age']['value']) + '\n' +
                                            "Emotion: " +  str(semotion) + '\n' +
                                            "Brille: " +  str(sglass) + '\n' +
                                            "Ethnie: " + str(translate.translate(str(details['faces'][0]['attributes']['ethnicity']['value']).encode('utf-8'))) + '\n\n' +                                          
                                            "Ich bin mir mit meiner Analyse zu " + str(details['faces'][0]['attributes']['facequality']['value']) +'% sicher'))
                
                    if smile > 40.1:
                        self.sender.sendMessage(str("Schön, dass du auf dem Bild lächelst! Das gefällt mir 😊 "))

                    log(message='faceanalyze' + ' from ' + username + '\n', path=logfile, terminal=False)

                except Exception as e:
                    #if any error accured in the try-block
                    self.sender.sendMessage(str("Es ist nicht deine Schuld. \nAber ich konnte kein Gesicht erkennen 😔\nVielleicht ist auch die Datei zu groß? (2 MB)")) 
                    log(message='Error: ' + unicode(e).encode("utf-8") + '\n', path=errorfile, terminal=True)


            elif content_type == 'text':			
                input = msg['text'].encode("utf-8").split('@')[0]	#.split returns a list ->[0] for the first element of the list (essential for chatgroups)

				#command: /start (shown to all users if they start a new conversation)
                if input == '/help' or input == '/start':
                    self.sender.sendMessage(str('Hi, ich bin Susan. Ich bin nicht so ganz ein Mensch wie du, aber ich versuche, so menschlich wie möglich zu sein. Dazu verwende ich Machine-Learnig.' + 
											                     ' Ich werde anfangs sicher ein paar Fehler machen, bitte verzeihe mir 😁'))
                    self.sender.sendMessage(str('Du kannst mir aber dabei helfen besser zu werden, indem du mit mir schreibst und dich nicht über meine Fehler ärgerst. \nDankeschön 😘' ))
                    self.sender.sendMessage(str('Dir gefällt dieser Bot? Dann bewerte mich doch bitte hier mit 5 Sternen: https://telegram.me/storebot?start=suusanbot'))

				#command: /credits
                elif input == '/credits':
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Conversational engine:\nChatterbot', url='https://github.com/gunthercox/ChatterBot')],
                    [dict(text='Telegrambot API:\nTelepot', url='https://github.com/nickoala/telepot')],
                    [dict(text="GIF's:\ngiphypop", url='https://github.com/shaunduncan/giphypop')],
                    [dict(text='Translation:\nGoogle Translate', url='https://github.com/MrS0m30n3/google-translate')],
                    [dict(text='Bilder:\nGoogle Bilder', url='https://github.com/hardikvasa/google-images-download/blob/master/google-images-download.py')],
                    [dict(text='Gesichtsanalyse:\nFace++', url='https://faceplusplus.com')],
                    [dict(text='Integration, Tools, Anpassungen und der Rest: @ThomasKoscheck', url='https://github.com/ThomasKoscheck/Telegrambots')],                    
                    ])
                    self.sender.sendMessage('Nur mit Hilfe verschiedene fantastische Teile von freier und offener Software konnte ich zu dem werden, was ich heute bin. Hier ist die vollständige Auflistung.', reply_markup=markup)

				#command: /knowledge
                elif input == '/knowledge':          
                    self.sender.sendMessage(str("Konversation: Ich kann ausgehend von Deinem Input eine (meist) sinnvolle Antwort geben."))
                    self.sender.sendMessage(str("Bilder: Wenn du mich nach Bilder fragst, kann ich dir ausgehend von der Google-Bildersuche ein Bild schicken. (z.B: 'Zeige mir ein Bild von Ziegen')"))
                    self.sender.sendMessage(str("Videos: Wenn du mich nach Videos fragst, kann ich dir ausgehend von der YouTubesuche ein Video schicken. (z.B: 'Zeige mir ein Video von Julien Bam')"))
                    self.sender.sendMessage(str("GIF's: Wenn du mich nach GIF'S fragst, kann ich dir ausgehend von der Datenbank giphy.com ein GIF schicken. (z.B: 'Zeige mir ein GIF von Star Wars')"))	
                    self.sender.sendMessage(str("Übersetzungen: Ich kann dir jede Sprache nach Deutsch übersetzen (z.B: Was bedeutet Hi, I am a cat)"))
                    self.sender.sendMessage(str("Gesichtsanalyse: Ich kann Daten wie Geschlecht, Emotion oder Alter anhand der Bilder, die du mir schickst erraten"))

                #command: /tools
                elif input == '/tools':
                    markup = ReplyKeyboardMarkup(keyboard=[
                     [KeyboardButton(text='/würfeln')],   
                     #[KeyboardButton(text='/zeit'), KeyboardButton(text='/würfeln')],      
                     ])
                    self.sender.sendMessage('Auflistung an kleinen Features, dich ich beherrsche', reply_markup=markup)

                #command: /würfeln
                elif input == '/würfeln':                  
                   self.sender.sendMessage(str(random.randint(1,6)), reply_markup=removemarkup)   

				#command: /akzeptieren
                elif input == '/akzeptieren':
                    if userCheck(chat_id): #user already in database
                        self.sender.sendMessage(str('Du hast den Haftungsausschluss bereits akzeptiert 👌'))
                    else:
                        self.sender.sendMessage(str('Du hast den Haftungsausschluss akzeptiert. Hier kannst Du ihn dir in Ruhe durchlesen: https://www.thomaskoscheck.de/projekte/telegrambot/haftungsausschluss.php'))
                        log(str(chat_id) + ', ' + firstname + ', ' + username + '\n', disclaimer)


				#chatfunction
                elif not input.startswith('/') and userCheck(chat_id): #and is_chatting:	no /command, user is already in database and is_chatting is true (/chat was executed)						
                    action = self.findActionWord(input, username)     #checks if specialaction was accomplished

                    if action == False:		#no special action was accomplished, telegrambot should answer conversational now
                        response = susan.get_response(input)	

                        #sending conversational response in telegram
                        self.sender.sendMessage(unicode(response).encode("utf-8"), reply_markup=removemarkup)

				#user not registered
                elif userCheck(chat_id) == False:
                    self.sender.sendMessage(str('Du bist leider kein registrierter Benutzer! 😔'))
                    self.sender.sendMessage(str('Registrieren kannst du dich, in dem du den Haftungsausschluss mit /akzeptieren annimmst.'))

			#user sent something that isnt text
            else:
                self.sender.sendMessage(str('Bisher verstehe ich nur Textnachrichten und Bilder 😔'))
                self.sender.sendMessage(str('Das wird sich in Zukunft aber sicher ändern!'))

        except Exception as e:
			#if any error accured in the try-block
            self.sender.sendMessage(str("Es ist nicht deine Schuld. \nAber bei mir ist etwas schief gelaufen. 😔 "))
            log(message='Error: ' + unicode(e).encode("utf-8") + ' : ' + time.strftime("%d.%m.%Y %H:%M") + '\n', path=errorfile, terminal=True)
            # + ' : ' + username + ' : ' + time.strftime("%d.%m.%Y %H:%M")
	

TOKEN = 'your-bot-token'

#creating the bot
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, ChatHandler, timeout=30
    ),
])

#run the loop forever
bot.message_loop(run_forever='Listening ...')