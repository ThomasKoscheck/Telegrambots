#Face++ - wwwfaceplusplus.com
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


    
