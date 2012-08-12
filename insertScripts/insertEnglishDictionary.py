#!/usr/bin/python
import sys
import os

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

def mongoInserter(p, collection, word, pho):
    ''' Inserts the word and its phonetic representation into a new mongo document. '''
    
    record = {'word' : word,
              'pho'  : pho}
    
    try:
        if collection.find(record).count() > 0:
            res = 0
        else:
            res = collection.insert(record)
    
    except Exception, e:
        handleErrors(p, e)
        res = None
        
    return res

#----------------------------------------------------------------------------------------

def main(configFile):
    ''' Holds it all together '''
    
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)

    # Handle the mongo connection and authentication
    c, dbh, collection, emoCollection = getMongoHandles(p)

    # Open the english dictionary file and loop it
    try:
        f = open(os.path.join(p.sourcePath, p.enPlainFile), 'r')
    except Exception, e:
        handleErrors(p, e)
    
    i = 1
    
    for line in f:
        
        # Tidy up before dealing with the words
        try:
            line = line.rstrip('\n').rstrip('\r')
            line = line.split(',')
            word, pho = line[0], line[1]
            
        except Exception, e:
            handleErrors(p, e) 
                   
        word = decodeEncode(word.lower())
        pho  = decodeEncode(pho)
        
        # Pass to mongo inserter
        res = mongoInserter(p, collection, word, pho)

        # Counter
        i += 1
        if p.verbose == True and i % 1000 == 0:
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
