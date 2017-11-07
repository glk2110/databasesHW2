#!/usr/bin/env python

from googleapiclient.discovery import build
import sys
from bs4 import BeautifulSoup
import urllib
import re
from NLPCore import NLPCoreClient

def isVisible(input1):
	if input1.parent.name in ['style', 'script', 'head', 'title', '[document]']:
		return False
	elif re.match('<!--.*-->', str(input1.encode('utf-8'))):
		return False
	else:
		return True

def makeQuery(apiKey, engineID, relation, threshold, query, k):
	if int(relation) == 1:
		relationName = "Live_In"
	elif int(relation) == 2:
		relationName = "Located_In"
	elif int(relation) == 3:
		relationName = "OrgBased_In"
	else:
		relationName = "Work_For"

	print("Parameters:")
	print("Client Key	= " + apiKey)
	print("Engine Key 	= " + engineID)
	print("Relation 	= " + relationName)
	print("Threshold 	= " + str(threshold))
	print("Query 		= " + query)
	print("# of tuples 	= " + str(k))
	iterationNum = 1
	goodTuples = 0
	extractedRelations = 0
	totalExtractedRelations = 0
	tuples = {}
	while goodTuples < int(k):
		totalExtractedRelations = goodTuples
		service = build("customsearch", "v1",
		developerKey=apiKey)

		res = service.cse().list(
			q=query,
			cx=engineID,
		).execute()
		print("=========== Iteration: " + str(iterationNum) + " - Query: " + query + " ===========")
		for i in range(10):
			solution = res[u'items'][i][u'link'].encode('ascii','ignore')
			print("Processing: " + solution)
			try:
				r = urllib.urlopen(solution).read()
			except Exception as e:
				print("Program could not extract text content from this web site; moving to the next one...")
				continue
			soup = BeautifulSoup(r)
			texts = soup.find_all(['h1','h2','h3','p'])
			result = []
			for text in texts:
				result.append(text.text.encode('ascii','ignore'))
			result = ["William Henry Gates III (born October 28, 1955) is an American business magnate, investor, author, philanthropist, and co-founder of the Microsoft Corporation along with Paul Allen.[2][3]","In 1975, Gates and Allen launched Microsoft, which became the world's largest PC software company. During his career at Microsoft, Gates held the positions of chairman, CEO and chief software architect, while also being the largest individual shareholder until May 2014.[4][a] Gates stepped down as chief executive officer of Microsoft in January 2000, but he remained as chairman and created the position of chief software architect for himself.[7] In June 2006, Gates announced that he would be transitioning from full-time work at Microsoft to part-time work and full-time work at the Bill & Melinda Gates Foundation.[8] He gradually transferred his duties to Ray Ozzie and Craig Mundie.[9] He stepped down as chairman of Microsoft in February 2014 and assumed a new post as technology adviser to support the newly appointed CEO Satya Nadella.[10]"]
			client = NLPCoreClient('stanford-corenlp-full-2017-06-09')
			properties1 = {
				"annotators": "tokenize,ssplit,pos,lemma,ner", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			properties2 = {
				"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=result, properties=properties1)
			print(doc.sentences[0].relations[0])
			print(doc.tree_as_string())
			print("Relations extracted from this website: " + str(extractedRelations) + " (Overall: " + str(totalExtractedRelations) + ")")
		iterationNum += 1
		goodTuples = 100

def main():
	# Build a service object for interacting with the API. Visit
	# the Google APIs Console <http://code.google.com/apis/console>
	# to get an API key for your own application.
	apiKey = sys.argv[1]
	engineID = sys.argv[2]
	relation = sys.argv[3]
	threshold = sys.argv[4]
	query = sys.argv[5]
	k = sys.argv[6]
	makeQuery(apiKey, engineID, relation, threshold, query, k)

if __name__ == '__main__':
	main()
