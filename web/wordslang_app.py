# Standard
import json
import sys
import os

#============================================================================================

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)


def local_on_error(errFile='errors.txt', message=None):
    ''' Handles an error message '''
    
    f = open(os.path.join(wsDir, errFile), 'a')
    f.write(message + '\n')
    f.close()

#============================================================================================
# TO ENSURE ALL OF THE FILES CAN SEE ONE ANOTHER.
try:
        
    # Find out whats in this directory recursively
    for root, subFolders, files in os.walk(wsDir):
        # Loop the folders listed in this directory
        for folder in subFolders:
            directory = os.path.join(root, folder)
            if directory.find('.git') == -1:
                sys.path.append(directory)
    
except:
    local_on_error(message='failed do the sys.path append.\n')

#============================================================================================
    
# BOTTLE AND CUSTOM LIBRARY IMPORTS
     
try:
    import bottle
    from bottle import route, run, request, abort, error, static_file
except:
    local_on_error(message='failed import of bottle.')
    
# Custom
try:
    from baseUtils import getConfigParameters, getMongoHandles, handleErrors, decodeEncode
    import mdb
except:
    local_on_error(message='failed import of baseUtils and mdb.\n')

# Custom
try:
    from wordslang_functions import *
except:
    local_on_error(message='failed wordslang supporting functions\n')

#============================================================================================
# CONFIG FILE WHEN RUN FROM DOTCLOUD

# Config information from a relative path
configPath = os.path.join(wsDir, 'config')
configFile = os.path.join(configPath, 'wordslang.cfg')

try:
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)
except Exception, e:
    local_on_error(message='%s \n failed on getConfigParameters.\n' %e)
    
# Handle the mongo connection and authentication
try:
    c, dbh, collection, emoCollection = getMongoHandles(p)
except Exception, e:
    local_on_error(message='Failed to get mongo handles.\n')

#////////////////////////////////////////////////////////////////////////////////////
#                                 URL PATHS BELOW
#////////////////////////////////////////////////////////////////////////////////////

#------------------------------------------------------------------------------------

@route('/test', method='GET')
def get_test():
    return json.dumps({'hello':'foobar'})


#------------------------------------------------------------------------------------

@route('/', method='GET')
@route('/home', method='GET')
@route('/index', method='GET')
def homePage():
    ''' The wordslang home page'''
    return static_file('index.html', root=os.path.join(wsDir, 'static/'))

#------------------------------------------------------------------------------------

@route('/examples', method='GET')
def examplesPage():
    ''' The wordslang examples page'''
    return static_file('examples.html', root=os.path.join(wsDir, 'static/'))

#------------------------------------------------------------------------------------

@route('/credits', method='GET')
def creditsPage():
    ''' Some of the credits for the data'''
    return static_file('credits.html', root=os.path.join(wsDir, 'static/'))

#------------------------------------------------------------------------------------

@route('/distinctdump')
def word_dump():
    '''Just does distinct dumping of words, pho and slang.'''

    validChecks  = ['word', 'pho', 'slang', 'emo']
    
    # Get the checks and output
    try:    check = request.query.check.lower()
    except: abort(400, 'No check specified. \n Options: check=%s' %('|'.join(validChecks)))
    print 'Check after the try/except:', check
    
    # Make sure they conform
    if check not in validChecks:
        abort(400, 'No check specified. \n Options: check=%s' %('|'.join(validChecks)))
    
    print 'Check after the check if:', check
    
    results = submitDistinctQuery(dbh, p, collection, emoCollection, check=check)
    
    return results
    
#------------------------------------------------------------------------------------------------

@route('/static/<filepath:path>')
def server_static(filepath):
    ''' Route to serve up the static files'''
    print p.webStaticRoute, filepath
    
    #return static_file(filepath, root='/Users/brantinghamr/Documents/Code/eclipseWorkspace/eventigram/dev/app/static/')
    return static_file(filepath, root=p.webStaticRoute)

#------------------------------------------------------------------------------------

@route('/ws')
@route('/wordslang/')
@route('/wordslang')
def word_check():
    '''    '''
        
    paramOptions = ['exists', 'all', 'word', 'slang', 'pho', 'emo']
    
    # The input token that the user wants to search for   
    token = request.query.token.lower()
 
    # What to check the token against
    check = request.query.check.lower()
    if check not in paramOptions[1:]:
        abort(400, 'No check specified. \n Options: check=%s' %('|'.join(paramOptions[1:])))

    # The type of the output (pho, word, slang)
    output  = request.query.output.lower()
    if output not in paramOptions[:-1]:
        abort(400, 'No output specified. \n Options: output=%s' %('|'.join(paramOptions[:-1])))
 
    try:
        regex = bool(request.query.regex)
    except:
        regex = None

    # Get the results in the correct format
    results = submitQuery(dbh, p, collection, emoCollection, token=token, flds=paramOptions,
                          check=check, output=output, regex=regex)
        
    return results
 
#------------------------------------------------------------------------------------

@route('/putemo', method='PUT')
@route('/postemo', method='POST')
def updateEmoPut():
    '''# Accept a list/array of pairs: [{"smile":":-)"},{"smile",":-]"}] '''
    
    data = request.body.read()
    if not data:
        abort(400, 'No data received')
    
    update = json.loads(data)
    
    results = []
    for item in update:
        word, token = item['word'], item['emo'] 
        
        success = mongoUpdate(emoCollection, word, 'emo', token)
        
        if success != None:
            res = {"word":word, "emo":token, "update":"1"}
        else:
            res = {"word":word, "emo":token, "update":"0"}
        
        results.append(res)
        
    return json.dumps(results)  

#------------------------------------------------------------------------------------

@route('/putslang', method='PUT')
@route('/postslang', method='POST')
def updateSlangPut():
    '''# Accept a list/array of pairs: [{"hello":"hi"},{"hello","yo"}] '''
    
    data = request.body.read()
    if not data:
        abort(400, 'No data received')
    
    update = json.loads(data)
    
    results = []
    for item in update:
        word, token = item['word'], item['slang'] 
        
        success = mongoUpdate(collection, word, 'slang', token)
        
        if success != None:
            res = {"word":word,"slang":token,"update":"1"}
        else:
            res = {"word":word,"slang":token,"update":"0"}
        
        results.append(res)
        
    return json.dumps(results)    

#------------------------------------------------------------------------------------
        
"""
if __name__ == '__main__':

    # Config information from a relative path
    configPath = os.path.join(wsDir, 'config')
    configFile = os.path.join(configPath, 'testsWordslang.cfg')

    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)
    
    # Handle the mongo connection and authentication
    c, dbh, collection, emoCollection = getMongoHandles(p)

    run(host='localhost', port=8044)
"""