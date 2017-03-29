#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chatterbot import ChatBot
import telepot
from telepot.delegate import per_chat_id, create_open, pave_event_space
import logging
import time
import codecs
import sys
import re
import os

#own sripts (must be in the same folder)
import imagescraper     #returns photos
import giphy    #returns gif's
import translate    #translates into german
import video  #returns videos

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None) #utf8mb4 activate

#chat is active
is_chatting = True

#path and name of the disclaimer 
disclaimer = 'disclaimer.txt'

#insert valid database URI here
db_uri="mongodb://your_mongodatabase_uri_here"

#insert database name here
db_name="your_mongodatabase_name_here

#used for special actions
Zeige = ['zeige', 'zeig', 'schicke', 'schick','sende', 'schreibe', 'schreib']
Bilder = ['bilder','bild', 'foto', 'photo']
Gif = ['gif', 'gifs']
Translate = ['\xc3\x9cbersetze', 'bedeutet', 'heißt']
Video = ['video', 'videos', 'clip', 'clips', 'film', 'filme', 'youtubevideo', 'youtubevideos']

# Uncomment the following line to enable verbose logging
# logging.basicConfig(level=logging.INFO)

#Create a new instance of a ChatBot
susan = ChatBot("Susan", 
			  storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
			  
			  logic_adapters=["chatterbot.logic.MathematicalEvaluation", 
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

def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

# function to save log messages to specified log file/print it to terminal
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
		return index, 'vom 
	
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

						success = self.sendFoto('jpg')
						if success == True:		#images was sent successful
							self.sender.sendMessage(str("So, hier ein Bild " + pronomen + "'" + input[index:].encode('utf-8') + "'"))	
						log(message = "Bildersuche mit '" + (input[index:]).encode('utf-8') + "'" + " from " + username + "\n", path=logfile)
						return True																														
																											
					count2 += 1

				#sending gifs
				count2 = 0
				while count2 < len(Gif):
					if Gif[count2] in str(input.lower()): #checks if input contains any words from Gif[]
				
						index, pronomen = findePronomen(input)
					
						giphy.downloadGif(input[index:].encode('utf-8'), chat_id)
						success = self.sendFoto('gif')
						if success == True:		#gif was sent successful
							self.sender.sendMessage(str("Hier, ein GIF " + pronomen + "'" + input[index:].encode('utf-8') + "'"))
						log(message = "GIFsuche mit '" + (input[index:]).encode('utf-8') + "'" + " from " + username + "\n", path=logfile)	
						return True			

					count2 += 1	
				
				#sending videos
				count2 = 0
				while count2 < len(Gif):
					if Video[count2] in str(input.lower()): #checks if input contains any words from Videos[]
				
						index, pronomen = findePronomen(input)
						result = video.fetch_youtube_url(input[index:].encode('utf-8')) #hands over the searchterm to video.py, getting link to video back

						self.sender.sendMessage(result, str("Hier, ein Video mit den Stichworten " + "'" +  input[index:].encode('utf-8') + "'"))					
						log(message = "Videosuche mit '" + (input[index:]).encode('utf-8') + "'" + " from " + username + "\n", path=logfile)	
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
				log(message = "Übersetzung von '" + (input[index:]).encode('utf-8') + "'" + " from " + username + "\n", path=logfile)	
				return True	

		if Translate[1] in str(input.lower()):  #checks if input contains any words from Translate[]								
			index = input.find('bedeutet') + 9						
			translation = translate.translate(input[index:].encode('utf-8'))					
			if translation == input[index:].encode('utf-8'): #translation was from german to german -> no translation needed
				return False
			else:				
				self.sender.sendMessage(str("'" + input[index:].encode('utf-8') + "' bedeutet: " + translation))
				log(message = "Übersetzung von '" + (input[index:]).encode('utf-8') + "'" + " from " + username + "\n", path=logfile)	
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
				return false	#error sending a gif

		else:
			try:
				self.sender.sendPhoto(open('tmp/'  + str(chat_id) + '/image.' + str(filetype)))
				os.system('rm -r tmp/' + str(chat_id))	
				return True

			except:        
				self.sender.sendMessage('Hmm, da habe ich nichts gefunden. Zum Trost ein Bild von einer Katze.')
				self.sender.sendPhoto(open('tmp/katze.jpg'))
				return false	#error sending an image
			      
    def on_chat_message(self, msg):
		global chat_id
		global is_chatting 
		is_chatting = True
		content_type, chat_type, chat_id = telepot.glance(msg)
		reload(sys)
		sys.setdefaultencoding("utf-8")

		try:			
			chat_id = msg['chat']['id']
			firstname = msg['from']['first_name'].encode('utf8')
			username = msg['from']['username'].encode('utf8')
			#group_name = msg['chat']['title']	
		
			if content_type == 'text':
				input = msg['text'].encode("utf-8").split('@')[0]	#.split returns a list ->[0] for the first element of the list (essential for chatgroups)

				#command: /start (shown to all users if they start a new conversation)
				if input == '/help' or input == '/start':
					self.sender.sendMessage(str('Hi, ich bin Susan. Ich bin nicht so ganz ein Mensch wie du, aber ich versuche, so menschlich wie möglich zu sein. Dazu verwende ich Machine-Learnig.' + 
											 ' Ich werde anfangs sicher ein paar Fehler machen, bitte verzeihe mir 😁'))
					self.sender.sendMessage(str('Du kannst mir aber dabei helfen besser zu werden, indem du mit mir schreibst und dich nicht über meine Fehler ärgerst. \nDankeschön 😘' ))
					self.sender.sendMessage(str('Dir gefällt dieser Bot? Dann bewerte mich doch bitte hier mit 5 Sternen: https://telegram.me/storebot?start=suusanbot'))
				
				#command: /credits
				elif input == '/credits':
					self.sender.sendMessage(str('Machine Learning/Conversational engine:\nChatterbot (https://github.com/gunthercox/ChatterBot)'))
					self.sender.sendMessage(str('Telegrambot API:\nTelepot (https://github.com/nickoala/telepot)'))
					self.sender.sendMessage(str("GIF's:\ngiphypop (https://github.com/shaunduncan/giphypop)"))
					self.sender.sendMessage(str('Translation:\nGoogle translate (https://github.com/MrS0m30n3/google-translate)'))
					self.sender.sendMessage(str('Bilder:\nGoogle Bilder (https://github.com/hardikvasa/google-images-download/blob/master/google-images-download.py)'))
					self.sender.sendMessage(str('Integration und der Rest: @ThomasKoscheck \n(https://github.com/ThomasKoscheck/Telegrambots)'))					
				
				#command: /knowledge
				elif input == '/knowledge':
					self.sender.sendMessage(str("Konversation: Ich kann ausgehend von Deinem Input eine (meist) sinnvolle Antwort geben."))
					self.sender.sendMessage(str("Bilder: Wenn du mich nach Bilder fragst, kann ich dir ausgehend von der Google-Bildersuche ein Bild schicken. (z.B: 'Zeige mir ein Bild von Ziegen')"))
					self.sender.sendMessage(str("Videos: Wenn du mich nach Videos fragst, kann ich dir ausgehend von der YouTubesuche ein Video schicken. (z.B: 'Zeige mir ein Video von Julien Bam')"))
					self.sender.sendMessage(str("GIF's: Wenn du mich nach GIF'S fragst, kann ich dir ausgehend von der Datenbank giphy.com ein GIF schicken. (z.B: 'Zeige mir ein GIF von Star Wars')"))
					self.sender.sendMessage(str("Übersetzungen: Ich kann dir jede Sprache nach Deutsch übersetzen (z.B: Was bedeutet Hi, I am a cat)"))

				#command: /akzeptieren
				elif input == '/akzeptieren':
					if userCheck(chat_id): #user already in database
						self.sender.sendMessage(str('Du hast den Haftungsausschluss bereits akzeptiert 👌'))
					else:
						self.sender.sendMessage(str('Du hast den Haftungsausschluss akzeptiert. Hier kannst Du ihn dir in Ruhe durchlesen: http://www.thomaskoscheck.tk/blog/projekte/susan/haftungsausschluss.html'))
						log(str(chat_id) + ', ' + firstname + ', ' + username + '\n', disclaimer)
			
				#command: /chat
				elif input == '/chat':
					is_chatting = True
					self.sender.sendMessage(str('Chatfunktion aktiviert. Deaktivieren mit /stopchat'))
					time.sleep(1)
					self.sender.sendMessage(str('Hallo ') + firstname +  str(', fantastisch etwas von dir zu lesen!'))

				#command: /stopchat
				elif input == '/stopchat':
					is_chatting = False
					self.sender.sendMessage(str('Bis bald ') + firstname + str(' !'))		

				#chatfunction
				elif not input.startswith('/') and userCheck(chat_id) and is_chatting:	#no /command, user is already in database and is_chatting is true (/chat was executed)						
					action = self.findActionWord(input, username)     #checks if specialaction was accomplished
			
					if action == False:		#no special action was accomplished, telegrambot should answer conversational now
						response = susan.get_response(input)

						#logging of input, response and user
						log(message='input: ' + input + ' from ' + username + '\n', path=logfile, terminal=True)    #named arguments
						log(message='response: ' + unicode(response).encode("utf-8") + '\n', path=logfile, terminal=True)		

						#sending conversational response in telegram
						self.sender.sendMessage(unicode(response).encode("utf-8"))

				#is_chatting == false
				elif not input.startswith('/') and userCheck(chat_id) and is_chatting == False:	#no /command, user is already in database and is_chatting is false (/stopchat was executed)
					self.sender.sendMessage(str('Wenn du die Chatfunktion aktivieren willst, benutze /chat!'))

				#user not registered
				elif userCheck(chat_id) == False:
					self.sender.sendMessage(str('Du bist leider kein registrierter Benutzer! 😔'))
					self.sender.sendMessage(str('Den Haftungsausschluss kannst du mit /akzeptieren annehmen.'))

			#user sent something that isnt text
			else:
				self.sender.sendMessage(str('Bisher verstehe ich nur Textnachrichten 😔'))
				self.sender.sendMessage(str('Das wird sich in Zukunft aber sicher ändern!'))
			
		except Exception as e:
			#if any error accured in the try-block
			self.sender.sendMessage(str("Es ist nicht deine Schuld. \nAber bei mir ist etwas schief gelaufen. 😔 "))
			print 'Error ' + str(e)

TOKEN = 'your_telegram_bot_id_here'

#creating the bot
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, ChatHandler, timeout=30
    ),
])

#run the loop forever
bot.message_loop(run_forever='Listening ...')

