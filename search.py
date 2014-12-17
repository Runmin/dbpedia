import urllib
import re
import HTMLParser
import webbrowser
import sys

from urllib import quote_plus
from httplib import HTTPConnection
from getopt import getopt,GetoptError

reload(sys)
sys.setdefaultencoding("utf-8")
entity_result = []
abstract_list = []
class GoogleParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.handle_starttag = self.main_start
        self.handle_data = self.main_data
        self.handle_endtag = self.main_end

    def main_start(self, tag, attrs):
        if tag == "li" and len(attrs) > 0 and attrs[0] == ("class", "g"):
            self.title = ""
            self.url   = ""
            self.text  = ""
            self.handle_starttag = self.li_start
            self.handle_data = self.li_data
            self.handle_endtag = self.li_end

    def main_data(self, data):
        pass

    def main_end(self, tag):
        pass
    # <li class="g"> ... </li>

    def li_start(self, tag, attrs):
        if tag == "h3":
            self.handle_starttag = self.h3_start
            self.handle_data = self.h3_data
            self.handle_endtag = self.h3_end
        elif tag == "div":
            self.handle_starttag = self.div_start
            self.handle_data = self.div_data
            self.handle_endtag = self.div_end

    def li_data(self, data):
        pass

    def li_end(self, tag):
        if tag == "div":
            parse_google_entry(self.title, self.url, self.text)
            self.handle_starttag = self.main_start
            self.handle_data = self.main_data
            self.handle_endtag = self.main_end
    # <h3> ... </h3>

    def h3_start(self, tag, attrs):
        if tag == "a":
            self.url = attrs[0][1]

    def h3_data(self, data):
        self.title += data

    def h3_end(self, tag):
        if tag == "h3": 
            self.handle_starttag = self.li_start
            self.handle_data = self.li_data
            self.handle_endtag = self.li_end
    # <div> ... </div>

    def div_start(self, tag, start):
        if tag == "br":
            self.handle_starttag = self.li_start
            self.handle_data = self.li_data
            self.handle_endtag = self.li_end

    def div_data(self, data):
        self.text += data

    def div_end(self, tag):
        pass

def parse_google_entry(title, url, text):
    global entity_result
    entity_result.append(title)

def change_initial_to_upper(key_word): #key_word is a string
    key_list = key_word.split(' ')
    word_list = []
    for word in key_list:
        title_word = word.title()
	#print word
        word_list.append(title_word)
    join_word = "_".join(word_list)
    #print join_word
    return join_word

def change_all_to_upper(key_word):
    return key_word.upper() 

def get_first_sentence(sen):
    sen_list = sen.split('.')
    return_sen = ""
    for s in sen_list:
	if len(return_sen) < 50:
		return_sen += s
    return return_sen

def rm_parenthesis(txt):
    new_txt = re.sub(r'\[[^()]*\]',"",txt)
    txt = re.sub(r'\([^()]*\)',"",new_txt)
    return txt

def rm_defined_pattern(txt):
    txt = re.sub(r'no\.|No\.',"no#",txt)
    return txt
	
def overlapping_word(abstract_hash):
    count = 0
    match =""
    word_list = ""
    for key in abstract_hash:
	if count == 0:
	    match = abstract_hash[key]
            #print "match is " + match
            word_list = match.split(' ')
 	    count +=1
        else:
            save_list = []
	    against = abstract_hash[key]
            if len(against)< 1:
		continue
            #print "against is : " + against
            against = against.split(' ') 
            for word in word_list:
                if word in against:
			#print "true" + word
			save_list.append(word)
	    word_list = save_list
    #print "[overlapping_word] result"
    return word_list
    
def overlapping_abstract():
    global abstract_list
    count = 0
    match =""
    word_list = ""
    #print "[overlapping_abstract]"
    for key in abstract_list:
	if count == 0:
	    match = key
            #print "match is " + match
            word_list = match.split(' ')
 	    count +=1
        else:
            save_list = []
	    against = key
            if len(against)< 1:
		continue
            #print "against is : " + against
            against = against.split(' ') 
            for word in word_list:
                if word in against:
			#print "true" + word
			save_list.append(word)
	    word_list = save_list
    return word_list

def rm_defined_word(word_list):
    new_list = []
    black_list = ['-','was','or','that','with','to','it','in','its','is','a','an','the','and','by','as']
    for word in word_list:
	if word not in black_list and word not in new_list:
		new_list.append(word)
    return new_list

def rm_coma(sen):
    new_sen = re.sub(r','," ",sen)
    return new_sen

def rm_last_s_and_space(sen):
    new_list = []
    word_list = sen.split(' ')
    for x in word_list:
	if x == "" or len(x)<=2:
		continue
	elif x[-1] == "s" and x[-2] !='i':
		s = x[:-1]
                new_list.append(s)
        else:
		new_list.append(x)
    return " ".join(new_list)

def check_if_disambiguous(html):
    l = parse_abstract(html)
    if len(l) > 1:
	return False
    else:
	return True


def parse_out_url(html):
    result = re.search(r'xmlns:dbpedia-owl="http:\/\/dbpedia.org\/ontology\/".*<small>',html)
    if result == None:
	return ""
    url = result.group(0)
    result = re.search(r'href=.*',url)
    url = result.group(0)
    url = url[6:-9]
    return url

def go_to_top_link(html):
    #print "go to top link"
    url =  parse_out_url(html)
    if url == "":
	return ""    
    conn = urllib.urlopen(url)
    html = conn.read()
    abstract= parse_abstract(html)    
    return abstract

def parse_abstract(html):
    global abstract_list

    abstract = get_abstract(html)
#    print abstract
    if abstract != "":
   	 abstract_list.append(abstract.lower())
    succinct_abstract = rm_parenthesis(abstract)
    succinct_abstract = rm_defined_pattern(succinct_abstract)
    #print "[parse_dbpedia]" + succinct_abstract
    first_sentence = get_first_sentence(succinct_abstract)
    first_sentence = rm_coma(first_sentence)
    first_sentence = rm_last_s_and_space(first_sentence)
    #print "[parse_dbpedia]" + first_sentence
    return first_sentence

def parse_dbpedia(key_word):
    print "key word is " + key_word
    url = "http://dbpedia.org/page/"
    url += key_word
    #print "[parse_dbpedia] URL:" + url
    print key_word
    conn = urllib.urlopen(url)
    html = conn.read()
    html = html 
    if check_if_disambiguous(html):
	sen = go_to_top_link(html)
        return sen.lower()
    else:
        first_sentence = parse_abstract(html)
        return first_sentence.lower()

def test_go_top_link():
    key_word = 'ACM'
    parse_dbpedia(key_word)

def print_hash(hash_input):
    for key in hash_input:
	print key + ":"
        print hash_input[key]

def understand_list_word(list_key_word):
    abstract_hash= {}
    for key_word in list_key_word:
	search_word = key_word
	if '_' not in key_word:
        	search_word = change_initial_to_upper(key_word)
	result = parse_dbpedia(search_word)
	#print "length is " + str(len(dum))
        if len(result) < 1:
		#print "Enter ALL Upper Case"
		result = parse_dbpedia(key_word.upper())
        abstract_hash[key_word] = result
    #print_hash(abstract_hash)
    l = overlapping_word(abstract_hash)    
    l = rm_defined_word(l)
    if (len(l) <=2):
       l = overlapping_abstract()
       l = rm_defined_word(l)
    l.insert(0,'wikipedia')
    print " ".join(l)
    return l

def get_abstract(html):
    pattern = "<p>"
    match = re.search(r'<p>.*<\/p>', html)  
    result = match.group(0)
    result = result.replace("<p>","")
    result = result.replace("</p>","")
    return result    


def parse_entity_result():
    global entity_result
    print "The result returned by google is:"
    for sen in entity_result:
	s = re.sub(r' - Wiki.*',"",sen)
        print s

def change_into_google_string(string_list):
    new_list = []
    for word in string_list:
	if word != "":
		new_list.append(word)
    sen = "+".join(new_list)
    return sen

def search_google_and_return_title(string_list,length):
    url = "/search?num=%s&q=" %(length)
    #url = "/search?q="
    #print url
    search  = change_into_google_string(string_list)
    url += search
    print "url is " + url
    conn = HTTPConnection("www.google.com")
    conn.request("GET", url)
    resp = conn.getresponse()  
    content = resp.read()
    parser = GoogleParser()
    parser.feed(content)
    return ""

#t = change_initial_to_upper('Alien_(film)') #key_word is a string
"""
key_word = "roger federer"
t = change_initial_to_upper(key_word) #key_word is a string
print t

html = "afdadsfasdf<p>roger federer</p>"
c = get_abstract(html)
print c
"""
if len(sys.argv) < 3:
    print "Need a query length argument"
    sys.exit()

length = sys.argv[1]
key_word_list = []

for i in range(2,len(sys.argv)):
    key_word_list.append(sys.argv[i])
print key_word_list

"""
key_word_list = ["ACM","IEEE"]

key_word_list = ["Tennis","Basketball","Soccer"]
key_word_list = ["Ferrari","Aston Martin"]
key_word_list = ["kobe byrant","allen iverson"]
key_word_list = ["ucla","ucsd","ucsb","ucb"]
key_word_list = ["roger federer","rafael nadal"]
key_word_list = ["Harvard University","Stanford University"]
key_word_list = ["Bill Gates","Steven Jobs"]
key_word_list = ["Barack Obama","George Washington"]
key_word_list = ["Brad Pitt","Tom Hanks"]
"""

#test_go_top_link()
#sys.exit()
l = understand_list_word(key_word_list)
search_google_and_return_title(l,length)
parse_entity_result()
