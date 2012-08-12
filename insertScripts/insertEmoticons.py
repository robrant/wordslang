#!/usr/bin/python
import sys
import os
import logging
import ConfigParser
import re

#============================================================================================
# TO ENSURE ALL OF THE FILES CAN SEE ONE ANOTHER.

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)

# Find out whats in this directory recursively
for root, subFolders, files in os.walk(wsDir):
    # Loop the folders listed in this directory
    for folder in subFolders:
        directory = os.path.join(root, folder)
        if directory.find('.git') == -1:
            sys.path.append(directory)

#============================================================================================

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

def mongoUpdate(p, collection, word, token):
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
    up = {'$addToSet':{'emo':token}}
    
    try:
        response = collection.update(q, up)
    
    except Exception, e:
        response = None
        handleErrors(p, e)

    return response

#----------------------------------------------------------------------------------------

def getDespaced(slang):
    ''' Removes spaces and returns slang(s) as a list'''

    # Add the existing slang to a list
    slangs = [slang]
    
    # Remove all spaces from the slang term and add that to the list too
    while slang.find(' ') >= 0:
        slang = slang.replace(' ', '')

    if slang not in slangs:
        slangs.append(slang)

    return slangs

#----------------------------------------------------------------------------------------

def main(configFile):
    ''' Holds it all together '''
    
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)

    # Handle the mongo connection and authentication
    c, dbh, collection, emoCollection = getMongoHandles(p)

    # Open the english dictionary file and loop it
    try:
        f = open(os.path.join(p.sourcePath, p.emoticons), 'r')
    except Exception, e:
        handleErrors(p, e)
    
    i = 1
    
    for line in f:
        
        # Tidy up before dealing with the words
        try:
            line = line.rstrip('\n').rstrip('\r')
            line = line.lstrip(',').rstrip(',')
            line = line.split(',')
        except Exception, e:
            handleErrors(p, e) 
        
        # Split up the line and take the first 2 columns           
        try:
            word, token = line[0], line[1] 
        except Exception, e:
            handleErrors(p, "\nLine:\n%s\n\n" %line) 
                
        # Handle the decoding/encoding for mongo           
        word   = decodeEncode(word.lower())
        token  = decodeEncode(token)
        
        # Drop the lead and end spaces and make it a list
        token = token.strip()
        
        # Get the space-removed emoticons
        tokens = getDespaced(token)
        tokens += getDespaced(token.lower())
        
        # Pass to mongo inserter
        for token in tokens:
            res = mongoUpdate(p, emoCollection, word, token)

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
    
    main(configFile)
