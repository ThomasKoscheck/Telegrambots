# Face++ - wwwfaceplusplus.com
# -*- coding: utf-8 -*-
import requests
import urllib2
import json
import os
import time
from shutil import copyfile

key = "API-Key"
secret = "API-Secret"

def getdetails(chat_id, imagepath):
    #open image send to susan (currently in /tmp)
    image = open(imagepath,'rb').read()

    files = {
        #'Content-Type': 'multipart/form-data',
        'image_file' : image
        }   

    payload = {
        'api_key' : key,
        'api_secret' : secret,
        'return_attributes' : 'age,gender,smiling,eyestatus,glass,emotion,ethnicity,facequality'
    }

    try: 
        # send request to faceplusplus api
        result = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect', params=payload, files=files).json()  

        # get unequivocal name (image id) from faceplusplus
        imageid= result[u'image_id']

        # get actual time, format: 06.02.2014 20:49:56
        atime = str(time.strftime("%d.%m.%Y %H-%M-%S"))

        # create directory where results are saved (json and image)
        directory = '/var/www/telegrambot/susan/data/' + str(chat_id) + '/' + str(atime) + '/'
        if not os.path.isdir(directory):
            os.makedirs(directory)
         
        # write to json file with unequivocal name (image id)
        with open(directory + 'details.json', 'w') as f:
            json.dump(result, f)

        # copy image from /tmp and save in same folder, delete /tmp file
        copyfile(imagepath, directory + 'image.jpg')
        os.system('rm -r tmp/' + str(chat_id) + '.jpg')	

        # return facedetails
        #send request to faceplusplus api
        result = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect', params=payload, files=files).json()  

        #get unequivocal name (image id) from faceplusplus
        imageid= result[u'image_id']
       
        # delete /tmp file
        os.system('rm -r tmp/' + str(chat_id) + '.jpg')	

        #return facedetails
        return result

    except urllib2.HTTPError as e:
        print e.read()
