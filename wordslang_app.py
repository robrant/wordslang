# Config information from a relative path
configFile = '/home/dotcloud/code/config/wordslang.cfg'

# Standard
import json
import sys
import os

def on_error(errFile='errors.txt', message=None):
    ''' Handles an error message '''
    
    f = open(os.path.join('/home/dotcloud/code/', errFile), 'a')
    f.write(message + '\n')
    f.close()
        
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

#------------------------------------------------------------------------------------

def checkAll(collection, flds, token):
    
    ''' Queries every field in the mongo document for the token.'''
    
    # Master list to hold all results - from all field queries
    results = []
    
    # Loop the fields and query each one
    for fld in flds:
        # Build the query json and find it
        q = {fld:token}
        res = collection.find(q)
        for r in res:
            del r['_id']
            results.append(r)
        
    return results

#----------------------------------------------------------------------------------------

def mongoUpdate(collection, word, slang):
    ''' Inserts the word and its phonetic representation into a new mongo document. '''
    
    # The query condition for the update
    query = {'word' : word}
    
    # Just in case the word doesn't already exist, create a new dictionary item with it, so that it maps to the emoticon/slang
    try:
        exists = collection.find(query).count()
        if exists == 0:
            collection.insert(query)
    except:
        response = None   
    
    # Adds to the list if slang isn't already present
    update = {'$addToSet':{'slang':slang}}
    
    try:
        response = collection.update(query, update, safe=True)
    except:
        response = None

    return response    

#------------------------------------------------------------------------------------

def checkLengthForExists(results):
    ''' Checks the length of results for 'exists' output type'''
    
    if len(results) == 0:
        results = {"exists":"false"}
    else:
        results = {"exists":"true"}

    return results

#------------------------------------------------------------------------------------

def submitQuery(collection, token, flds, check, output):
    '''Query mongo with query and optionally just count.'''

    # Check against every field to see if it exists in it
    if check == 'all':
        results = checkAll(collection, flds, token.lower())
        
        if output == 'exists':
            results = checkLengthForExists(results)
        # Return complete documents
        elif output == 'all':
            if len(results) == 0:
                results = {}
        
        # Check all fields, output just 'ouput' selection 
        else:
            out = []
            for document in results:
                out.append({output:document[output]})
            results = out
            
    # Query the specific field specified in 'check'
    else:
        results = []
        res = collection.find({check : token.lower()})
        for r in res:
            del r['_id']
            results.append(r)
        
        # Just return whether it exists
        if output == 'exists':
            results = checkLengthForExists(results)

        # Return complete documents
        elif output == 'all':
            if len(results) == 0:
                results = {}
            
        # Output is either pho, word or slang, so just extract that field
        else:
            out = []
            for document in results:
                out.append({output:document[output]})
            results = out
            
    return json.dumps(results)

#------------------------------------------------------------------------------------

@route('/ws')
@route('/wordslang/')
@route('/wordslang')
def word_check():
    '''    '''
        
    paramOptions = ['exists', 'all', 'word', 'slang', 'pho']
    
    # The input token that the user wants to search for   
    token = request.query.token.lower()
 
    # What to check the token against
    check = request.query.check.lower()
    if check not in paramOptions[1:]:
        abort(400, 'No check specified. \n Options: check=%s' %('|'.join(paramOptions[1:])))

    # The type of the output (pho, word, slang)
    output  = request.query.output.lower()
    if output not in paramOptions:
        abort(400, 'No output specified. \n Options: output=%s' %('|'.join(paramOptions)))
 
    # Get the results in the correct format
    results = submitQuery(collection, token=token, flds=paramOptions, check=check, output=output)
        
    return results

 
#------------------------------------------------------------------------------------

@route('/test', method='GET')
def get_test():
    return json.dumps({'hello':'foobar'})

#------------------------------------------------------------------------------------

@route('/putslang', method='PUT')
@route('/putslang', method='POST')

def updateSlangPut():
    '''# Accept a list/array of pairs: [{"hello":"hi"},{"hello","yo"}] '''
    
    data = request.body.read()
    if not data:
        abort(400, 'No data received')
    
    update = json.loads(data)
    
    results = []
    for item in update:
        word, slang = item['word'], item['slang'] 
        
        success = mongoUpdate(collection, word, slang)
        
        if success != None:
            res = {"word":word,"slang":slang,"update":"1"}
        else:
            res = {"word":word,"slang":slang,"update":"0"}
        
        results.append(res)
        
    return json.dumps(results)    

#------------------------------------------------------------------------------------
        
"""
if __name__ == '__main__':

    # Config information from a relative path
    configFile = '../config/wordslang.cfg'
    
    # Get the config information into a single object. p also gets passed into the listener
    p = getConfigParameters(configFile)
    
    # Handle the mongo connection and authentication
    c, dbh, collection = getMongoHandles(p)

    run(host='localhost', port=8044)
"""