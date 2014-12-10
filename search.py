import urllib
import re

def change_initial_to_upper(key_word): #key_word is a string
    key_list = key_word.split(' ')
    word_list = []
    for word in key_list:
        title_word = word.title()
        word_list.append(title_word)
    join_word = "_".join(word_list)
    return join_word

def change_all_to_upper(key_word):
    return key_word.upper() 

def get_first_sentence(sen):
    sen_list = sen.split('.')
    return sen_list[0]

def rm_parenthesis(txt):
    new_txt = re.sub(r'\[[^()]*\]',"",txt)
    txt = re.sub(r'\([^()]*\)',"",new_txt)
    return txt

def rm_defined_pattern(txt):
    txt = re.sub(r'no.|No.',"no#",txt)
    return txt
	
def overlapping_word(abstract_hash):
    count = 0
    match =""
    word_list = ""
    for key in abstract_hash:
	if count == 0:
	    match = abstract_hash[key]
            word_list = match.split(' ')
 	    count +=1
        else:
            save_list = []
	    against = abstract_hash[key]
            print "against is : " + against 
            for word in word_list:
                if word in against:
			print "true" + word
			save_list.append(word)
	    word_list = save_list
    print "[overlapping_word] result"
    print "* " + " ".join(word_list)
    
def parse_dbpedia(key_word):
    url = "http://dbpedia.org/page/"
    url += key_word
    print "[parse_dbpedia] URL:" + url
    conn = urllib.urlopen(url)
    html = conn.read()
    abstract = get_abstract(html)
    print abstract
    succinct_abstract = rm_parenthesis(abstract)
    succinct_abstract = rm_defined_pattern(succinct_abstract)
    #print "[parse_dbpedia]" + succinct_abstract
    first_sentence = get_first_sentence(succinct_abstract)
    print "[parse_dbpedia]" + first_sentence
    return first_sentence

def print_hash(hash_input):
    for key in hash_input:
	print key + ":"
        print hash_input[key]


def understand_list_word(list_key_word):
    abstract_hash= {}
    for key_word in list_key_word:
        search_word = change_initial_to_upper(key_word)
	result = parse_dbpedia(search_word)
	#print "length is " + str(len(dum))
        if len(result) < 1:
		print "Enter ALL Upper Case"
		result = parse_dbpedia(key_word.upper())
        abstract_hash[key_word] = result
    #print_hash(abstract_hash)
    overlapping_word(abstract_hash)    

def get_abstract(html):
    pattern = "<p>"
    match = re.search(r'<p>.*<\/p>', html)  
    result = match.group(0)
    result = result.replace("<p>","")
    result = result.replace("</p>","")
    return result    

def do_get_selection_element_list(input_list,s_list,index,num_ele,total,result):
    #print "index = " + str(index) + "num_ele "
    if num_ele == total and index <= len(input_list):
     #   print "found!!!"
     #   print s_list
        result.append(s_list)
    elif index >=len(input_list):
        return
    else:
    #    print "s_list with index = " + str(index)
    #    print s_list
        save1 = []
        save2 = []
        copy_list(s_list,save1)
        copy_list(s_list,save2)
        do_get_selection_element_list(input_list,save1,index+1, num_ele,total,result)
        save2.append(input_list[index])
        do_get_selection_element_list(input_list,save2,index+1,num_ele+1,total,result)
        return
"""
key_word = "roger federer"
t = change_initial_to_upper(key_word) #key_word is a string
print t

html = "afdadsfasdf<p>roger federer</p>"
c = get_abstract(html)
print c
"""
key_word_list = ["ucla","ucsd","ucsb","ucb"]
key_word_list = ["Ferrari","Aston Martin","Porsche"]
key_word_list = ["ACM","IEEE"]
key_word_list = ["kobe byrant","allen iverson"]

key_word_list = ["roger federer","rafael nadal", "novak djokovic"]

understand_list_word(key_word_list)
