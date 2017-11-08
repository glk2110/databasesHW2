#!/usr/bin/env python

from googleapiclient.discovery import build
import sys
from bs4 import BeautifulSoup
import urllib
import re
from NLPCore import NLPCoreClient
import operator

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
	tuples = set()
	queries = set()
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
			extractedRelations = 0
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
			properties = {
				"annotators": "tokenize,ssplit,pos,lemma,ner", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			properties2 = {
				"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=result, properties=properties)
			goodSentences = []
			for sen in doc.sentences:
				tok1 = False
				tok2 = False
				if int(relation) == 1:
					for re in sen.tokens:
						if re.ner == "PERSON":
							tok1 = True
						elif re.ner == "LOCATION":
							tok2 = True
				elif int(relation) == 2:
					for re in sen.tokens:
						if re.ner == "LOCATION" and tok1 == False:
							tok1 = True
						elif tok1 == True and re.ner == "LOCATION":
							tok2 = True
				elif int(relation) == 3:
					for re in sen.tokens:
						if re.ner == "ORGANIZATION":
							tok1 = True
						elif re.ner == "LOCATION":
							tok2 = True
				else:
					for re in sen.tokens:
						if re.ner == "PERSON":
							tok1 = True
						elif re.ner == "ORGANIZATION":
							tok2 = True
				if tok1 == True and tok2 == True:
					goodSentences.append(sen)
			finalSentences = []
			for sentence in goodSentences:
				newsentence = ""
				for x in sentence.tokens:
					newsentence += " " + x.word.encode('ascii','ignore')
				finalSentences.append(newsentence)
			doc2 = client.annotate(text=finalSentences, properties=properties2)
			list1 = []
			list2 = []
			for s1 in doc2.sentences:
				list1.append(s1)
			for s3 in list1:
				counterr = 0
				for s4 in s3.relations:
					if counterr == 2:
						break
					counterr += 1
					if relationValid(s4, relation, relationName):
						print("=============== EXTRACTED RELATION ===============")
						extractedRelations += 1
						newsentence1 = ""
						for x1 in s3.tokens:
							newsentence1 += " " + x1.word
						print("Sentence: " + newsentence1)
						confidence = s4.probabilities[relationName]
						enTy1 = s4.entities[0].type
						enVa1 = s4.entities[0].value
						enTy2 = s4.entities[1].type
						enVa2 = s4.entities[1].value
						print("RelationType: " + relationName + " | Confidence= " + confidence + " | EntityType1= " + enTy1 + " |")
						print("EntityValue1= " + enVa1 + " | EntityType2= " + enTy2 + " | EntityValue2= " + enVa2 + " |")
						print("============== END OF RELATION DESC ==============")
						if(float(confidence) >= float(threshold) and float(confidence) >= float(s4.probabilities["Live_In"]) and float(confidence) >= float(s4.probabilities["OrgBased_In"]) and float(confidence) >= float(s4.probabilities["Located_In"]) and float(confidence) >= float(s4.probabilities["Work_For"])):
							tuples.add((relationName, round(float(confidence),3), enTy1, enVa1, enTy2, enVa2))
			totalExtractedRelations += extractedRelations
			print("Relations extracted from this website: " + str(extractedRelations) + " (Overall: " + str(totalExtractedRelations) + ")")
		print("Pruning relations below threshold...")
		goodTuples = len(tuples)
		print("Number of tuples after pruning: " + str(goodTuples))
		print("================== ALL RELATIONS =================")
		myTuples = list(tuples)
		myTuples.sort(key=operator.itemgetter(1), reverse = True)
		count = 0
		queries.add(query)
		for tup in myTuples:
			if(count == 0 and enVa2 + " " + enVa1 not in queries):
				query = enVa2 + " " + enVa1
				count = 1
			print("RelationType: " + tup[0] + "  | Confidence: " + str(tup[1]) + "		| Entity #1= " + tup[3] + " (" + tup[2] + ")	| Entity #2: " + tup[5] + " (" + tup[4] + ")")
		if(count==0):
			print("All possible queries have already been used! Breaking Program")
			goodTuples = 1000
		iterationNum += 1

def relationValid(relation, re, reName):
	type1 = relation.entities[0].type
	type2 = relation.entities[1].type
	if int(re) == 1:
		if((type1 == "PEOPLE" and type2 == "LOCATION") or (type1 == "LOCATION" and type2 == "PEOPLE")):
			if(float(relation.probabilities[reName])>=float(relation.probabilities["Live_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Located_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Work_For"]) and float(relation.probabilities[reName])>=float(relation.probabilities["OrgBased_In"])):
				return True
	elif int(re) == 2:
		if((type1 == "LOCATION" and type2 == "LOCATION")):
			if(float(relation.probabilities[reName])>=float(relation.probabilities["Live_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Located_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Work_For"]) and float(relation.probabilities[reName])>=float(relation.probabilities["OrgBased_In"])):
				return True
	elif int(re) == 3:
		if((type1 == "ORGANIZATION" and type2 == "LOCATION") or (type1 == "LOCATION" and type2 == "ORGANIZATION")):
			if(float(relation.probabilities[reName])>=float(relation.probabilities["Live_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Located_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Work_For"]) and float(relation.probabilities[reName])>=float(relation.probabilities["OrgBased_In"])):
				return True
	else:
		if((type1 == "PEOPLE" and type2 == "ORGANIZATION") or (type1 == "ORGANIZATION" and type2 == "PEOPLE")):
			if(float(relation.probabilities[reName])>=float(relation.probabilities["Live_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Located_In"]) and float(relation.probabilities[reName])>=float(relation.probabilities["Work_For"]) and float(relation.probabilities[reName])>=float(relation.probabilities["OrgBased_In"])):
				return True
	return False

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
