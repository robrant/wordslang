#!/usr/bin/python
import sys
import logging
import ConfigParser
import os

from baseUtils import getConfigParameters, getMongoHandles, handleErrors, decodeEncode
import mdb

'''
- Get config 
- Connect to mongo
- Authenticate with mongo
- Open main dictionary file
- Loop content
- build document
- Insert document 

'''

#----------------------------------------------------------------------------------------

def mongoUpdate(p, collection, word, slang):
    ''' Inserts the word and its phonetic representation into a new mongo document. '''
    
    # The query condition for the update
    q = {'word' : word}
    
    # Just in case the word doesn't already exist, create a new dictionary item with it, so that it maps to the emoticon/slang
    try:
        exists = collection.find(q).count()
        if exists == 0:
            collection.insert(q)
        
    except Exception, e:
        handleErrors(p, e)   
    
    # Adds to the list if slang isn't already present
    up = {'$addToSet':{'slang':slang}}
    
    try:
        collection.update(q, up)
    
    except Exception, e:
        handleErrors(p, e)
        
    return

#----------------------------------------------------------------------------------------

def main(configFile, file='norm'):
    ''' Holds it all together '''
    
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)

    # Handle the mongo connection and authentication
    c, dbh, collection = getMongoHandles(p)

    if file == 'norm':
        fileToProcess = p.enNormalisedFile
    elif file == 'slang':
        fileToProcess = p.slangFile

    # Open the english dictionary file and loop it
    try:
        f = open(os.path.join(p.sourcePath, fileToProcess), 'r')
    except Exception, e:
        print e
        handleErrors(p, e)
    
    i = 1
    
    for line in f:
        
        # Tidy up before dealing with the words
        try:
            line = line.rstrip('\n').rstrip('\r')
            line = line.split(',')
            slang, word = line[0], line[1]
        except Exception, e:
            handleErrors(p, e)
                   
        word = decodeEncode(word.lower())
        slang  = decodeEncode(slang.lower())
        
        # Pass to mongo inserter
        res = mongoUpdate(p, collection, word, slang)

        # Counter
        i += 1
        if p.verbose == True and i % 100 == 0:
            print i

    f.close()
    mdb.close(c, dbh)
        
        
#----------------------------------------------------------------------------------------

if __name__ == '__main__':
        
    # Command Line arguments
    configFile = sys.argv[1]
    
    # first argument is the config file path
    if not configFile:
        print 'no Config file provided. Exiting.'
        sys.exit()
    
    main(configFile, norm=True)
