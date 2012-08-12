import json

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

def mongoUpdate(collection, word, field, token):
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
    update = {'$addToSet':{field:token}}
    
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

def checkEmo(emoCollection, token):
    '''Checks for the existence of the word in an emoticon collection'''
    
    # The query condition for the update
    query = {'emo' : token}
    
    # Just in case the word doesn't already exist, create a new dictionary item with it, so that it maps to the emoticon/slang
    try:
        res = emoCollection.find(query)
        results = [r for r in res]
    except:
        results = None

    return results

#------------------------------------------------------------------------------------

def submitQuery(collection, emoCollection, token, flds, check, output, regex=None):
    '''Query mongo with query and optionally just count.'''

    if check == 'emo':
        results = checkEmo(emoCollection, token)
        
        if output == 'exists':
            results = checkLengthForExists(results)
        else:
            out = []
            for document in results:
                out.append({output:document['word']})
            results = out
            
    # Check against every field to see if it exists in it
    elif check == 'all':
        results = checkAll(collection, flds, token.lower())
        
        if output == 'exists':
            results = checkLengthForExists(results)
        # Return complete documents
        elif output == 'all':
            if len(results) == 0:
                results = []
        
        # Check all fields, output just 'ouput' selection 
        else:
            out = []
            for document in results:
                out.append({output:document[output]})
            results = out
            
    # Query the specific field specified in 'check'
    else:
        results = []
        
        # Allow for regex query
        print regex
        if regex == True:
            query = {check : {'$regex':'.*%s.*' %token.lower()}}
            print json.dumps(query)
        else:
            query = {check : token.lower()}

        res = collection.find(query)
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