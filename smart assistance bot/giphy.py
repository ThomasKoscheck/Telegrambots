#https://github.com/shaunduncan/giphypop

from giphypop import translate
import urllib
import os

def downloadGif(searchterm, chat_id): 
    try:
        os.system('mkdir tmp/' + str(chat_id))
    
        img = translate(searchterm.encode('utf-8'))   
        urllib.urlretrieve(img.fixed_height.downsampled.url, "tmp/" + str(chat_id) + "/image.gif")

    #when a error occurs (e.g. when nothing was found), a 404 Gif will be sent
    except:
        img = translate(searchterm.encode('utf-8'))   
        urllib.urlretrieve("https://media.giphy.com/media/fOltIlqkjBSaQ/giphy.gif", "tmp/" + str(chat_id) + "/image.gif")


