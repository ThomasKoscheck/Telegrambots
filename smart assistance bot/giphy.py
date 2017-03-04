#https://github.com/shaunduncan/giphypop

from giphypop import translate
import urllib
import os

def downloadGif(searchterm, chat_id): 
    try:
        os.system('mkdir tmp/' + str(chat_id))
    
        img = translate(searchterm.encode('utf-8'), api_key='dc6zaTOxFJmzC')   #api_key is the open public beta key
        urllib.urlretrieve(img.fixed_height.downsampled.url, "tmp/" + str(chat_id) + "/image.gif")

    #if an error occurred (eg. when nothing was found), an 404 GIF will be sent 
    except:
        img = translate(searchterm.encode('utf-8'))   
        urllib.urlretrieve("https://media.giphy.com/media/fOltIlqkjBSaQ/giphy.gif", "tmp/" + str(chat_id) + "/image.gif")


