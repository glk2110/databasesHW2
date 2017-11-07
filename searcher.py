#!/usr/bin/env python

from googleapiclient.discovery import build

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
	while goodTuples < k:
		service = build("customsearch", "v1",
		developerKey=apiKey)

		res = service.cse().list(
			q=query,
			cx=engineID,
		).execute()
		print("=========== Iteration: " + str(iterationNum) + " - Query: " + query + " ===========")
		for i in range(10):
			print("Result " + str(i + 1) + "\n")
			solution = res[u'items'][i][u'link'].encode('ascii','ignore')
			title =  res[u'items'][i][u'title'].encode('ascii','ignore')
			print(" URL: " +solution)
			print(" Title: "+ title)
			summary = res[u'items'][i][u'snippet'].encode('ascii','ignore')
			print(" Summary: " + summary)
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
