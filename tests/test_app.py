# Standard
import json
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


def on_error(errFile='errors.txt', message=None):
    ''' Handles an error message '''
    
    f = open(os.path.join('/home/dotcloud/code/', errFile), 'a')
    f.write(message + '\n')
    f.close()

def callExample(collection):
    '''    '''
    
    try:
        collection.insert({'callExample':'succeed'})
    except:
        on_error(message='failed to insert "callExampel".')
        
# FOSS
try:
    import bottle
    from bottle import route, run, request, abort, error
except:
    on_error(message='failed import of bottle.')
    
# Custom
try:
    from baseUtils import getConfigParameters, getMongoHandles, handleErrors, decodeEncode
    import mdb
except:
    on_error(message='failed import of baseUtils and mdb.\n')
    
# Config information from a relative path
configFile = '/home/dotcloud/code/config/wordslang.cfg'

try:
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)
except Exception, e:
    on_error(message='%s \n failed on getConfigParameters.\n' %e)
    
# Handle the mongo connection and authentication
try:
    c, dbh, collection = getMongoHandles(p)
except Exception, e:
    #on_error(message='db: %s host: %s port: %s user: %s pssd: %s \n' %(p.db, p.dbHost, p.dbPort, p.dbUser, p.dbPassword))
    on_error(message='Failed to get mongo handles.\n')
    #on_error(message='%s\n' %e)
    
@route('/check1')
def check1():
    '''    '''
    
    global c
    global dbh
    global collection
    #global p
    # It appears you don't need to make these global scope
    
    return str(p.dbUser) + '--' + str(p.dbPassword)

@route('/check2')
def check2():
    '''    '''
    
    global c
    global dbh
    global collection
    global p
    
    try:
        collection.insert({'hello':'world'})
    except:
        on_error('failed to insert into the database under check 2.\n')

@route('/check3')
def check3():
    '''    '''
    
    global collection
    
    try:
        collection.find({'hello':'world'})
    except:
        on_error('failed to retrieve document from the db. \n')
        
@route('/check4')
def check4():
    '''    '''
    
    global collection
    
    callExample(collection)
    
@route('/check5')
def check5():
        f = open('/home/dotcloud/code/output.txt', 'w')
        f.write(os.getcwd())
        return os.getcwd()
