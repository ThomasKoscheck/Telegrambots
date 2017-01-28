#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import datetime
import random
import datetime
import telepot
import os
import threading
import re
import codecs
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None) #utf8mb4 aktivieren

"""
After **inserting token** in the source code, run it:
```
$ python2.7 homebot.py
```
"""

def findWholeWord(w):	
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


#compares chat_id
def check_security():
		if chat_id == "your-chatid":
			return True
		else:
			return False

#waits for commands
def handle(msg):
	i = 1
	global chat_id 
	chat_id = msg['chat']['id']
	input = msg['text'].encode('utf-8')

	print 'Got input: %s' % input

	#initial text
	if input == '/start':
		bot.sendMessage(chat_id, str("Hi, ich bin @RaspbHome und bin für die Hausautomatisierung zuständig. Über /help kannst du dir alle Befehle anzeigen lassen, die ich bereits verstehe"))

	#status 
	elif input == "/status":
		if  check_security() == "True":
			bot.sendMessage(chat_id, str("Du bist autorisiert"))
		else:
			bot.sendMessage(chat_id, str("Du bist nicht autorisiert. Bitte melde dich an."))
	

	#showing all commands
	elif input == '/help':
		bot.sendMessage(chat_id, str("Bald verfügbar"))

	#displays eine random number
	elif input == '/roll':
		bot.sendMessage(chat_id, random.randint(1,6))
	
	#displays current time
	elif input == '/zeit':
		bot.sendMessage(chat_id, str("Es ist " + str(datetime.datetime.now())))

	#rebooting system
	elif input == '/reboot' and check_security():
			
		print "Das System wird neugestartet" 
		bot.sendMessage(chat_id, str('Das System wird neugestartet. Bis gleich!'))      
		os.system("sudo reboot now")
	
		
	#displays uptime
	elif input == '/sysuptime' and check_security():
		bot.sendMessage(chat_id, str(os.popen("uptime").read()))
	
	#runs a command
	elif Befehl[0] in str(input) and check_security():
		index = input.find('command') + 8		
		os.system(input[index:])
		bot.sendMessage(chat_id, str("Der Befehl '") + input[index:] + str("' wurde ausgeführt"))	

	#displays temperatur of the system
	elif input == '/systemp' and check_security():
		bot.sendMessage(chat_id, str(os.popen("vcgencmd measure_temp").read()))
	
	#displays system frequency
	elif input == '/systakt' and check_security():
		bot.sendMessage(chat_id, str(os.popen("vcgencmd measure_clock arm").read()))

	#enables the lights
	elif input == '/lichtan' and check_security():
		lichtstatus = os.popen("sudo gpio -g read 2").read()
		if int(lichtstatus) == 1:
			bot.sendMessage(chat_id, str('Das Licht ist bereits an'))
		else:
			os.system("sudo gpio -g mode 2 out")
			os.system("sudo gpio -g write 2 1")    
			bot.sendMessage(chat_id, str('Ich habe das Licht angeschaltet'))

	#disables the lights
	elif input == '/lichtaus' and check_security():
		lichtstatus = os.popen("sudo gpio -g read 2").read()
		if int(lichtstatus) == 0:
				bot.sendMessage(chat_id, str('Das Licht ist bereits aus'))
		else:
			os.system("sudo gpio -g mode 2 out")
			os.system("sudo gpio -g write 2 0")
			bot.sendMessage(chat_id, str('Ich habe das Licht ausgeschaltet'))

	#weathercast, doesn't work yet
	elif input == '/wetterbericht' and check_security():	
		  #displays the buttons
		  #markup = ReplyKeyboardMarkup(keyboard=[
					# ['Plain text', KeyboardButton(text='Text only')],
					# [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)], ])
		  markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Location', request_location=True)], ])
		  bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)


	#not authorized
	elif(check_security() == False):
		bot.sendMessage(chat_id, str("Du bist nicht autorisiert!"))
		bot.sendMessage(chat_id, str("Bitte melde dich an"))

	#no command
	else: bot.sendMessage(chat_id, str("Schön, dass du mit mir reden möchtest, aber ich verstehe das bisher noch nicht"))
		
print 'I am listening'
bot = telepot.Bot('your-bot-id')
bot.setWebhook()
bot.message_loop(handle)


while 1:
	time.sleep(10)
