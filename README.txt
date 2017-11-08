Project 2 Group 23

I am submitting three files. My searcher.py file and the two python wrapper files that were given to us called data.py and NLPCore.py

Our program can be run the same way as the given example program. go into the folder and run python searcher.py AIzaSyDlZ_2pBGPzkEekVenizjWW5j8Zt8akWsQ 001595247901778627873:pkx
qapndan4 4 .2 "bill gates microsoft" 10. Where the first parameter is the Client key, the second is the engine key, the third is the number corresponding to the relation of choice, the 4th parameter is the confidence threshold, the fifth is the desired query, and the 6th is the number of tuples desired. 

The internal design of our project is as follows. First we query google for the given query. Then we loop through those results and for each result we extract text from the website. We then look through all of that text using the first pipeline to determine if there is a possibility of a desired realtion in each sentence. If there is, we send that sentence through the second pipeline. If we find a relation that has a high enough confidence, we will add it to the tuples that are returned to the users. If after 10 websites are search there is still not enough tuples, we will create a new search with the query being the tuple with the highest confidence value. This will continue until there are enough tupels displayed to the user. We used python's beautiful soup to extract text from websites and the python wrapper given to us in the assignment. 

For step 3, we used urllib to open and read each website. We extracted the text using beautiful soup in python and converted the unicode to ascii string. We extracted h1, h2, h3 and p HTML tags. We then used the python wrapped to annotate the text. We first used the first pipeline to identify candidate sentences that may have relations we are interested in. Then we fed those sentences into the second pipeline. If we found relations above the confidence threshold, they were added to the list of good tuples. 

Our Google API key is AIzaSyDlZ_2pBGPzkEekVenizjWW5j8Zt8akWsQ. Our engine key is 001595247901778627873:pkxqapndan4.

Please be patient while running this assignment. It is not slow, but it does not print the relations until it is done with the website. The formatting is exactly the same as the sample assignment given to us. 