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
			client = NLPCoreClient('stanford-corenlp-full-2017-06-09')
			properties1 = {
				"annotators": "tokenize,ssplit,pos,lemma,ner", #Second pipeline; leave out parse,relation for first
				"ner.useSUTime": "0"
				}
			properties2 = {
				"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=result, properties=properties2)
			print(doc)
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
