Description
===========
This code does the following top level tasks:
1. Builds a mongo database
2. Reads a series of word-to-slang, word-to-phonetic and word-to-emoticon lists and stores them as mongo documents.
3. Builds a webservice for the querying and updating of the documents.

Purpose
=======

The aim of this work is to make it easy to retrieve different representations of standard english words through a web service.
It is hoped that some level of machine learning could contribute to the detection of new slang words and emoticons as they
appear in social media to improve and update the store.

This code was written to support the mining of social media content using text processing software. To extract the 
maximum useful content from social media, the content is often transformed from slang/abbreviation
terms into 'real' words. Several projects have attempted to document the mapping between words and slang terms, words
and emoticons. This code uses those initial datasets as a starting point for a web service, hopefully useful to 
anyone mining social media for useful content.

Going one stage further for those wishing to identify words based on their phonetic representation, this code
also includes the phonetic representation of words.

Mongo documents represent words, known tokens in the english language. Each word document has fields storing the word's
phonetic representation and a field storing an array of slang terms that are associated with the word. There is not a 1-1
mapping between a slang term and a word; a slang term may apply to more than one word (incidentally, this is one of the
main reasons for returning a list/array of json objects as the default). 

To ensure this was available permanently and as a learning experience, the code was hosted on dotcloud as a sandbox.

Web Service
============
A very simple web services is provided by python bottle and wsgi, running in nginx when deployed to dotcloud. 
Unit/functional tests are provided for the web parts to ensure the url parameters work, so check those for good examples.

There are 3 functional URL parameters. ALL ARE REQUIRED.

1. token: Is the term/word/character set that you wish to search for in the db.
		  Eg. /wordslang?token=smiiiillle 			--> search term is 'smiiiillle'

2. check: Is the field you want to search for that token in. The options are 'word','slang','pho' and 'all'. The latter checks each of the first 3.
		  Eg. /wordslang?token=smiiiillle&check=word	--> checks for 'smiiiillle' in the word field.
		   
3. output: Is the field you want returned. The options are 'word','slang','pho','all',exists'. Where all is specified, all fields will be returned.
		   Where 'exists' is specified, a {"exists":"true"} or {"exists":"false"} will be returned.
		   Eg. /wordslang?token=smiiiillle&check=word&output=pho		--> checks the word field for the term foo and outputs the phonetic representation of 'smile'.
		   
There are some POST/PUT hooks in for machine-based population of new word-slang combinations too, but they aren't tested.


Dotcloud Deployment
===================

The service deploys to dotcloud automatically, but the population of the database must be done manually under ssh with the server.
$ dotcloud ssh wordslang

It was hoped that even the database inserts could be automated but at the time, *nix 'at' was not supported on dotcloud and building it into the
postinstall made that fail due postinstall timeout limit (5 mins?). I looked into a kludge involving crons and then deleting the cron, but it
seems OTT.

The setupapp.py handles the setup of the mongo db (trivial), the building of the right indexes and some username and password configuration.
Specifically the configureDatabase.py extracts the admin password from the environment.json file built on the dotcloud server, uses that 
to authenticate against mongo, creates a new user/password and then writes that back to the main runtime config file for the other processes
to use.

Debugging bottle/wsgi was pretty tedious on dotcloud, possibly because I didn't fully understand where it would be writing its errors to.
I ended up using a combination of try/except and then error logging to a local file, which worked, but was klunky. 


Improvements
============
Here are some improvements I can/should make when time permits and based on whether it gets used.

- Error webpages and templates
- API explanation pages

- PUT/POST to a quarantene collection?
Deployment docs for Apache webserver
Deployment docs for nginx on dotcloud
Other datasets for inclusion?
Working with academic groups to build upon this list.
Including non-space separated versions of the emoticons - DONE.
Inclusion of a fuzzy/regex matching query for terms - with the speed costs that will have. Possibly just partial matching - wild card on the ends of words? 

Sources:

http://www.cool-smileys.com/text-emoticons-part1 & http://www.cool-smileys.com/text-emoticons-part2 for the emoticon lookup
