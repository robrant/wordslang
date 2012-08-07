import os
import mdb
import ConfigParser
import json

class getConfigParameters():
    ''' Gets the configuration parameters into an object '''
    
    def __init__(self, filePath):
        
        config = ConfigParser.ConfigParser()
        try:
            config.read(filePath)
        except Exception, e:
            print "Failed to read the config file for twitter connection client."
            print e
                
        # Mongo parameters
        self.dbHost     = config.get("backend", "host")
        self.dbPort     = config.getint("backend", "port")
        self.db         = config.get("backend", "db")

        self.dbUser     = config.get("backend", "user")
        self.dbPassword = config.get("backend", "password")
        self.collection = config.get("backend", "collection")
        self.indexes    = json.loads(config.get("backend", "indexes"))
        self.dropCollection = config.getboolean("backend", "drop_collection")

        # Base Dictionary to be used
        self.sourcePath       = config.get("source", "source_path")
        self.enPlainFile      = config.get("source", "en_plain")
        self.enNormalisedFile = config.get("source", "en_normalised")
        self.slangFile        = config.get("source", "en_slang")
        self.emoticons        = config.get("source", "emoticons")
        
        # Error Logging
        self.verbose   = config.getboolean("error", "verbose")
        self.writeOut  = config.getboolean("error", "write_out")    
        self.errorFile = config.get("error", "err_file")
        self.errorPath = config.get("error", "err_path") 

        # URL query parameter field/name
        self.qToken  = config.get("url", "token_query")
        self.qSlang  = config.get("url", "slang_query")
        self.qExists = config.get("url", "word_exists")        
        self.qPhone  = config.get("url", "phonetic_query")

#----------------------------------------------------------------------------------------

def getMongoHandles(p):
    ''' Gets the mongo connection handle, authentication and the collection handle.  '''

    # Handles the mongo connections
    c, dbh = mdb.getHandle(db=p.db, host=p.dbHost, port=p.dbPort)

    # Authentication
    try:
        auth = dbh.authenticate(p.dbUser, p.dbPassword)
    except Exception, e:
        print "Failed to authenticate with mongo db."
        print e

    collHandle = dbh[p.collection]
    
    return c, dbh, collHandle

#-------------------------------------------------------------------------------------

def handleErrors(p, error):
    ''' Handles the printing (or other) of errors. '''

    # Report out the parsing errors if verbose is set
    if p.verbose == True:
        print "-"*10+"Error"+"-"*10
        print error

    if p.writeOut == True:
        f = open(os.path.join(p.errorPath, p.errorFile), 'a')
        f.write(str(error)+'\n')
        f.close()
#----------------------------------------------------------------------------------------

def decodeEncode(token, encoding='latin-1'):
    ''' Holds it all together '''
    
    token = token.decode(encoding)
    token = token.encode('utf8')
    
    return token    
#-------------------------------------------------------------------------------------

