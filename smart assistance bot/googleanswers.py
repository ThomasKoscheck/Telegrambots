# https://github.com/Areeb-M/GoogleAnswers
import requests
from html.parser import HTMLParser

# Scraper.py
class Target:
    def __init__(self, elements):
        self.elements = elements

    def check_path(self, path):
        length = len(self.elements)
        for i in range(length):
            index = -length + i
            if path[index][0] == self.elements[index][0] and (path[index][1] == self.elements[index][1] or self.elements[index][1] == ''):
                continue
            else:
                return False
        return True


class Parser(HTMLParser):
    def __init__(self, target):
        HTMLParser.__init__(self)
        self.target = target
        self.target_depth = 0
        self.path = []
        self.occurrences = []

    def handle_starttag(self, tag, attributes):
        attr_string = ""
        for attribute in attributes:
            attr_string += attribute[0] + '="' + attribute[1] + '" '
        attr_string = attr_string[:-1]

        self.path.append([tag, attr_string])
        if self.target_depth > 0 or self.target.check_path(self.path):
            if self.target_depth == 0:
                self.occurrences.append('')
            self.target_depth += 1

    def handle_endtag(self, tag):
        self.path.pop()
        if self.target_depth > 0:
            self.target_depth -= 1

    def handle_data(self, data):
        if self.target_depth > 0:
            self.occurrences[-1] += data

    def feed(self, data):
        HTMLParser.feed(self, data)
        return self.occurrences


def scrape(url):
    try:
    	global HEADER_PAYLOAD, TARGET_LIST
    	data = requests.get(url, headers=HEADER_PAYLOAD).text   
    	start_js = data.index('/g-section-with-header') # changed
    	data = data[0:start_js]
    
    	results = []

    	for target in TARGET_LIST:
        	results += Parser(target).feed(data)
    	print(results)
    	return results

    except:
	results = ''
	return results


TARGET_LIST = [
    Target([['div', 'class="_XWk"']]),  # Enables Featured Snippet Scraping
    Target([['span', 'class="_Tgc"']]),  # Enables Featured Snippet Description Scraping
    Target([['span', 'class="cwcot" id="cwos"']]),  # Enables Calculator Answer Scraping
    Target([['div', 'class="vk_bk vk_ans"']])  # Enable Time Scraping
]

HEADER_PAYLOAD = {  # Enables requests.get() to See the Same Web Page a Browser Does.
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}

class Result:
    def __init__(self, query, scraper_results):
        self.query = query
        self.results = scraper_results

        if len(self.results) > 0:
            self.string = ''
            # for i in range(len(self.results)):
                # self.string += '[{0}] {1}'.format(i+1, self.results[i]).replace('  ', ' ')
            self.string = self.results[0].replace('  ', ' ')	# I want only one result

        else:
            self.string = ''

    def __str__(self):
        return self.string


def ask(query):
    url = convert_query(query)
    result = Result(query, scrape(url))
    print(result)
    return str(result)


def convert_query(query):
    result = query
    result = result.replace(' ', '+')
    result = result.replace('?', '') 
    result = "https://www.google.de/search?q=" + result
    return result




