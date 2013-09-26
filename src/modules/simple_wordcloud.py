# This ECA file parser uses PLY (Python Lex-Yacc)
# Please read http://www.dabeaz.com/ply/ply.html before changing this file.

import imp
import os
import operator
from collections import Counter
import ECA_parser
import actions
import fm

def init(arg):
	pass

# incomplete, there should be resources or a file search path
f = open('modules/stopwoorden.txt', 'r')
stop_words = [line.strip() for line in f]
tweets_words = ['http', 'amp']
stop_words += tweets_words
punctuation = "!\"$%&'()*+,-./:;<=>?[\]^_`{|}~'"  

def stopwords():
	return stop_words

def getwords(text):
	text = ''.join(ch for ch in text.lower() if ch not in punctuation) 
	words = text.split()
	counts = Counter(words)
	keys = list(counts.keys())
	for key in keys:
		if len(key) < 3 or key[0].isdigit() or key.startswith('http'):
			del counts[key]
	return [ v for v in counts]

def update_wordcloud(wc_id,d):
	top = None
	count = 0
	res = []
	for w in sorted(d, key=d.get, reverse=True): 
		if top:
			count += 1
			if count > 15:
				break
		else:
			top = d[w]
		tdict = {}
		tdict['text'] = w
		tdict['weight'] = int((d[w]/top)*15)
		res.append(tdict)
	# print(str(res))
	# return actions.create_wordcloud_gadget(wc_id,'myWordCloud','Bata Words',res)
	return actions.update_wordcloud_gadget(wc_id,res)

# A simple wordcloud class
class Wordcloud:
	def __init__(self,max_words):
		# print("#!CREATING A NEW WORDCLOUD")
		self.max_words = max_words
		self.tweet_buffer = ''

	def addText(self,tweet):
		self.tweet_buffer += tweet

	def getWordWeights(self):
		text = self.tweet_buffer.lower()
		text = ''.join(ch for ch in text if ch not in punctuation) 
		words = text.split()
		counts = Counter(words)
		for word in stop_words:
		        del counts[word]
		keys = list(counts.keys())
		for key in keys:
			if len(key) < 3 or key[0].isdigit() or key.startswith('http'):
				del counts[key]
		final = counts.most_common(self.max_words)
		max_count = max(final, key=operator.itemgetter(1))[1]
		final = [(name, count / float(max_count))for name, count in final]
		res = []
		for item in final:
			tdict = {}
			tdict['text'] = item[0]
			tdict['weight'] = int(item[1]*self.max_words)
			res.append(tdict)
		# print(res)
		res = []
		for item in final:
			tdict = {}
			tdict['text'] = item[0]
			tdict['weight'] = int(item[1]*self.max_words)
			res.append(tdict)
		return res

def createWordcloud(max_words):
	return Wordcloud(int(max_words))

wordcloud_functions = {
	"createWordcloud" : ( 1, fm.fcall1(createWordcloud)),
	"getwords" : ( 1, fm.fcall1(getwords)),
	"stopwords" : ( 0, fm.fcall0(stopwords)),
	"addText" : ( 2, fm.mcall2(Wordcloud.addText)),
	"update_wordcloud" : ( 2, fm.fcall2(update_wordcloud)),
	"getWordWeights" : ( 1, fm.mcall1(Wordcloud.getWordWeights)),
}

ECA_parser.functions.update( wordcloud_functions )

# Test function.
if __name__ == '__main__':
	print("#!TWORDCLOUD")
	wc = createWordcloud(15)
	wc.addText('@vessie @Tapz @Scarbir Ik ben in Enschede zaterdag! Batavierenrace. Veel plezier!')
	wc.addText('Ik heb dit weekend bijna 10km hardgelopen, dus vind eigenlijk wel dat ik volgend weekend naar het feestje vd #batavierenrace mag.')
	wc.addText('Bataradio doet live verslag Batavierenrace http://t.co/6FVfQE')
	wc.getWordWeights()
