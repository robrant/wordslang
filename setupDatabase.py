import sys

importDir = ['/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/tests/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/scripts/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/libs/']
for dirx in importDir:
    if dirx not in sys.path: sys.path.append(dirx) 

import mdb
from pymongo import DESCENDING, ASCENDING
from baseUtils import getConfigParameters, handleErrors

#------------------------------------------------------------------------

def main(configFile=None):
    ''' Builds the collections and indexes needed for the bam mongo work.
        # See also /src/tests/testMdb for full tests of the base functions. '''

    if not configFile:
        configFile = "/Users/brantinghamr/Documents/Code/eclipseWorkspace/wordslang/config/wordslang.cfg"
    
    # Get the config information into a single object
    p = getConfigParameters(configFile)

    # Get a db handle
    if p.verbose==True:
        print "---- Geting Mongo Handle."
    c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db)
    
    try:
        auth = dbh.authenticate(p.dbUser, p.dbPassword)
    except Exception, e:
        print "Failed to authenticate with mongo db."
        print e

    # Create the collection
    try:
        if p.dropCollection==True:
            if p.verbose==True: print "---- Dropping Collection."
            print "---- Creating Collection."
            dbh.drop_collection(p.collection)
        dbh.create_collection(p.collection)
    except Exception, e:
        handleErrors(p, e)

    # Collection handle
    collHandle = dbh[p.collection]

    # Create indexes
    if p.verbose==True: print "---- Create Plain Indexes."
    
    for index in p.indexes['plain']:
        collHandle.create_index([(index, ASCENDING)])

    if p.verbose==True: print "---- Create Compound Indexes."
    for index in p.indexes['compound']:
        pass
    
    mdb.close(c, dbh)
    
if __name__ == "__main__":
    main()