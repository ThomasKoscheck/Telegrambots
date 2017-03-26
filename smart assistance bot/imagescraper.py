#Searching and Downloading Google Images/Image Links
#https://github.com/hardikvasa/google-images-download/blob/master/google-images-download.py
import sys  
import time
import urllib2
import os


########### Edit From Here ###########

#This list is used to search keywords. You can edit this list to search for google images of your choice. You can simply add and remove elements of the list.
search_keyword = []

#This list is used to further add suffix to your search term. Each element of the list will help you download 100 images. First element is blank which denotes that no suffix is added to the search keyword of the above list. You can edit the list by adding/deleting elements from it.So if the first element of the search_keyword is 'Australia' and the second element of keywords is 'high resolution', then it will search for 'Australia High Resolution'
keywords = []

########### End of Editing ###########




#Downloading entire Web Document (Raw Page Content)
def download_page(url):
    version = (3,0)
    cur_version = sys.version_info
    if cur_version >= version:     #If the Current Version of Python is 3.0 or above
        import urllib.request    #urllib library for Extracting web pages
        try:
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
            req = urllib.request.Request(url, headers = headers)
            resp = urllib.request.urlopen(req)
            respData = str(resp.read())
            return respData
        except Exception as e:
            print(str(e))
    else:                        #If the Current Version of Python is 2.x
        import urllib2
        try:
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
            req = urllib2.Request(url, headers = headers)
            response = urllib2.urlopen(req)
            page = response.read()
            return page
        except:
            return"Page Not found"


#Finding 'Next Image' from the given raw page
def _images_get_next_item(s):
    start_line = s.find('rg_di')
    if start_line == -1:    #If no links are found then give an error!
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_line = s.find('"class="rg_meta"')
        start_content = s.find('"ou"',start_line+1)
        end_content = s.find(',"ow"',start_content+1)
        content_raw = str(s[start_content+6:end_content-1])
        return content_raw, end_content


#Getting all links with the help of '_images_get_next_image'
def _images_get_all_items(page):
    items = []
    while True:
        item, end_content = _images_get_next_item(page)
        if item == "no_links":
            break
        else:
            items.append(item)      #Append all the links in the list named 'Links'
            time.sleep(0.1)        #Timer could be used to slow down the request for image downloads
            page = page[end_content:]
    return items


############## Main Program ############
def search(image, chat_id):

	search_keyword = [image]
	#Download Image Links	
	items = []
	#iteration = "Item no.: " + str(1) + " -->" + " Item name = " + str(search_keyword[0])
	#print (iteration)
	#print ("Evaluating...")
	search_keywords = search_keyword[0]
	search = search_keywords.replace(' ','%20')
				
	url = 'https://www.google.com/search?q=' + search  + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
	raw_html =  (download_page(url))
	time.sleep(0.1)
	items = items + (_images_get_all_items(raw_html))
	
	#print ("Image Links = "+str(items))
	#print ("Total Image Links = "+str(len(items)))
	#print ("\n")	
	#print ("Starting Download...")

	# IN this saving process we are just skipping the URL if there is any error
	k=0
	errorCount=0
	from urllib2 import Request,urlopen
	from urllib2 import URLError, HTTPError

	try:
		req = Request(items[k], headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
		response = urlopen(req)

		#specific directory for download
		directory = 'tmp/' + str(chat_id) + '/'
		if not os.path.isdir(directory):
			os.makedirs(directory)

		output_file = open(directory + 'image'+".jpg",'wb')
		data = response.read()
		output_file.write(data)
		response.close();
		k=k+1;

	except IOError:   #If there is any IOError
		errorCount+=1
		print("IOError on image "+str(k+1))
		k=k+1;

	except HTTPError as e:  #If there is any HTTPError
		errorCount+=1
		print("HTTPError"+str(k))
		k=k+1;

	except URLError as e:
		errorCount+=1
		print("URLError "+str(k))
		k=k+1;

	#print("\n")
	#print("All are downloaded")
	#print("\n"+str(errorCount)+" ----> total Errors")

	#----End of the main program ----#