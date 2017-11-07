#!/usr/bin/env python

from googleapiclient.discovery import build
import sys
from bs4 import BeautifulSoup
import urllib

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
		for i in range(1):
			solution = res[u'items'][i][u'link'].encode('ascii','ignore')
			print("Processing: " + solution)
			r = urllib.urlopen(solution).read()
			soup = BeautifulSoup(r)
			texts = soup.findAll(text=True)
			result = filter(isVisible, texts)
			print(list(result))
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
