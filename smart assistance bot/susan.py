#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chatterbot import ChatBot
import logging
import telepot
import time
import codecs
import sys
import re
import os

#own scripts (need to be in the same folder)
import imagescraper     #images
import giphy    #GIF's
import translate    #translation 
import video  #videos


codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None) #utf8mb4 aktivieren

#path and name of the log file
logfile = 'logfile.log'

#path and name of the disclaimer
haftung = 'disclaimer.txt'

#Insert valid database URI here
db_uri= "your-mongodb-uri-here"

#Insert database name here
db_name="your-mongodb-database-name-here"

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

# function to save log messages to specified log file
def log(message, path):

	# open the specified log file
	file = open(path,"a")

	# write log message with timestamp to log file
	file.write(message)

	# close log file
	file.close

def usercheck():
	datafile = file('disclaimer.txt')
	found = False
	for line in datafile:
		if str(chat_id) in line:
			found = True
	return found

def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

#creates chat_id specific folder, downloads a photo into it, sends the photo and deletes the folder
def sendPhoto(filetype):
	if filetype == 'gif':
		try:
			bot.sendDocument(chat_id, open('tmp/'  + str(chat_id) + '/image.gif'))
			os.system('rm -r tmp/' + str(chat_id))	

		except:        
			bot.sendMessage('Hmm, da habe ich nichts gefunden. Zum Trost ein Bild von einer Katze.')
			bot.sendPhoto(chat_id, open('tmp/katze.jpg'))

	else:
		try:
			bot.sendPhoto(chat_id, open('tmp/'  + str(chat_id) + '/image.' + str(filetype)))
			os.system('rm -r tmp/' + str(chat_id))	

		except:        
			bot.sendMessage(chat_id, 'Hmm, da habe ich nichts gefunden. Zum Trost ein Bild von einer Katze.')
			bot.sendPhoto(chat_id, open('tmp/katze.jpg'))


#finding specialwords
def findActionWord(input):
	count = 0
		
	while count < len(Zeige):
		if Zeige[count] in str(input.lower()): #checks if input contains specialwords from Zeige[] 

			#sending photos
			count2 = 0													
			while count2 < len(Bilder):
				if Bilder[count2] in str(input.lower()): ##checks if input contains specialwords from Bilder[] 
					
					index, pronomen = findPronomen(input)

					filetype = imagescraper.search((input[index:]).encode('utf-8'), chat_id)    #calls imagescraper.py and passing searchquery
					sendPhoto(filetype)
					bot.sendMessage(chat_id, str("Hier, ein Bild " + pronomen + input[index:].encode('utf-8')))	
					return True																														
																											
				count2 += 1

			#sending GIF's
			count2 = 0
			while count2 < len(Gif):
				if Gif[count2] in str(input.lower()): ##checks if input contains specialwords from Gif[]
				
					index, pronomen = findPronomen(input)
					
					giphy.downloadGif(input[index:].encode('utf-8'), chat_id)
					sendPhoto('gif')
					bot.sendMessage(chat_id, str("Hier, ein GIF " + pronomen + input[index:].encode('utf-8')))	
					return True			

				count2 += 1	
				
			#sending videos
			count2 = 0
			while count2 < len(Gif):
				if Video[count2] in str(input.lower()): #checks if input contains specialwords from Video[] 
				
					index, pronomen = findPronomen(input)
					result = video.fetch_youtube_url(input[index:].encode('utf-8')) #passing searchquery to video.py, getting link back

					bot.sendMessage(chat_id, result)					
					bot.sendMessage(chat_id, str("Hier, ein Video mit dem Suchwort " +  input[index:].encode('utf-8')))	
					return True			

				count2 += 1	   																											
		count = count + 1																												
			
	count = 0
	count2 = 0

	#translation
	if Translate[0] in str(input.lower()): #checks if input contains specialwords from Translate[] 	
		index = input.find('\xc3\x9cbersetze') + 11			
		translation = translate.translate(input[index:].encode('utf-8'))	
		if translation == input[index:].encode('utf-8'): #no translation needed, input was already german
			return False
		else:				
			bot.sendMessage(chat_id, str("'" + input[index:].encode('utf-8') + "' bedeutet: " + translation))	
			return True	

	if Translate[1] in str(input.lower()): #checks if input contains specialwords from Translate[] 									
		index = input.find('bedeutet') + 9						
		translation = translate.translate(input[index:].encode('utf-8'))					
		if translation == input[index:].encode('utf-8'): #no translation needed, input was already german
			return False
		else:				
			bot.sendMessage(chat_id, str("'" + input[index:].encode('utf-8') + "' bedeutet: " + translation))	
			return True		

	return False

#finding and returning pronomen
def findPronomen(input):

	if findWholeWord('einem')(input.lower()):  
		index = input.find('einem') + 6
		return index, 'von einem '		

	elif findWholeWord('einer')(input.lower()): 
		index = input.find('einer') + 6
		return index, 'von einer '

	elif findWholeWord('von')(input.lower()):   		 
		index = input.find('von') + 4
		return index, 'von '
								

	elif findWholeWord('vom')(input.lower()):   					 
		index = input.find('vom') + 4
		return index, 'vom '

	
#Main loop
def handle(msg):
	reload(sys)
	sys.setdefaultencoding("utf-8")

	try:
		global chat_id 
		chat_id = msg['chat']['id']
		vorname = msg['from']['first_name'].encode('utf8')
		username = msg['from']['username'].encode('utf8')
		input = msg['text'].encode("utf-8")
		
		if input.startswith('/'):
			#command: /start (all users are seeing this on start)
			if input == '/help' or input == '/start':
				bot.sendMessage(chat_id, str('Hi, ich bin Susan. Ich bin nicht so ganz ein Mensch wie du, aber ich versuche, so menschlich wie möglich zu sein. Dazu verwende ich Machine-Learnig.' + 
											 ' Ich werde anfangs sicher ein paar Fehler machen, bitte verzeihe mir, aber ich bin noch klein und muss zuerst ganz viel lernen.'))
				bot.sendMessage(chat_id, str('Du kannst mir aber dabei helfen, in dem du mit mir schreibst und dich nicht über meine Fehler ärgerst. Dankeschön' ))

			#command: /credits
			elif input == '/credits':
				bot.sendMessage(chat_id, str('Machine Learning/Conversational engine: Chatterbot (https://github.com/gunthercox/ChatterBot)'))
				bot.sendMessage(chat_id, str('Telegrambot API: Telepot (https://github.com/nickoala/telepot)'))
				bot.sendMessage(chat_id, str("GIF's: giphypop (https://github.com/shaunduncan/giphypop)"))
				bot.sendMessage(chat_id, str('Translation: Google translate (https://github.com/MrS0m30n3/google-translate)'))
				bot.sendMessage(chat_id, str('Der Rest: @ThomasKoscheck (https://github.com/ThomasKoscheck)'))

			#command: /knowledge
			elif input == '/knowledge':
				bot.sendMessage(chat_id, str("Konversation: Ich kann ausgehend von Deinem Input eine (meist) sinnvolle Antwort geben."))
				bot.sendMessage(chat_id, str("Bilder: Wenn du mich nach Bilder fragst, kann ich dir ausgehend von der Google-Bildersuche ein Bild schicken. (z.B: 'Zeige mir ein Bild von Katzen')"))
				bot.sendMessage(chat_id, str("Videos: Wenn du mich nach Videos fragst, kann ich dir ausgehend von der YouTubesuche ein Video schicken. (z.B: 'Zeige mir ein Video von Julien Bam')"))
				bot.sendMessage(chat_id, str("GIF's: Wenn du mich nach GIF'S fragst, kann ich dir ausgehend von der Datenbank giphy.com ein GIF schicken. (z.B: 'Zeige mir ein GIF von Star Wars')"))
				bot.sendMessage(chat_id, str("Übersetzungen: Ich kann dir jede Sprache nach Deutsch übersetzen (z.B: Was bedeutet Hi, I am a cat)"))

			#command: /akzeptieren
			elif input == '/akzeptieren':
				if usercheck(): #user already exists
					bot.sendMessage(chat_id, str('Du hast den Haftungsausschluss bereits akzeptiert'))
				else:
					bot.sendMessage(chat_id, str('Du hast den Haftungsausschluss akzeptiert. Hier kannst Du ihn dir in Ruhe durchlesen: http://www.dein-haftungsausschluss.html'))
					log(str(chat_id) + ', ' + vorname + ', ' + username + '\n', haftung)


		elif usercheck():	
			
			action = findActionWord(input)     #checks in specialaction need to be done
			
			if action == False:		#no specialaction, bot should respond conversational
				response = susan.get_response(input)
			
				#sending the answer in telegram
				bot.sendMessage(chat_id, unicode(response).encode("utf-8"))

		else:
			bot.sendMessage(chat_id, str('Du bist leider kein registrierter Benutzer!'))
			bot.sendMessage(chat_id, str('Den Haftungsausschluss kannst du mit /akzeptieren annehmen.'))
			

	except Exception as e:
		#all errors are handled with this
		bot.sendMessage(chat_id, str("Hoppla, da ist ein Fehler aufgetreten. Verzeih mir und mach einfach weiter :)"))
		print 'Fehler bei: ' + input 
		print 'Error: ' + str(e)

bot = telepot.Bot('your-bot-id')
bot.setWebhook()
bot.message_loop(handle)

print 'I am listening ...'

while 1:
	time.sleep(10)

