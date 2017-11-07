#!/usr/bin/env python

from googleapiclient.discovery import build
import sys

def makeQuery(apiKey, engineID, relation, threshold, query, k):
	if relation == 1:
		relationName = "Live_In"
	elif relation == 2:
		relationName = "Located_In"
	elif relation == 3:
		relationName = "OrgBased_In"
	else:
		relationName = "Work_For"

	print("Parameters:")
	print("Client Key	= " + apiKey)
	print("Engine Key 	= " + engineID)
	print("Relation		= " + relationName)
	print("Threshold 	= " + str(threshold))
	print("Query 		= " + query)
	print("# of tuples 	= " + str(k))
	iterationNum = 1
	goodTuples = 0
	extractedRelations = 0
	totalExtractedRelations = 0
	while goodTuples < k:
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
