'''
Tests to be run:

- Build a small collection with a couple of chosen docs in it
- 
Hit the URL...
1.  - static response to test

ERRORS
2.  with no token - expect error back
3.  with no output
4.  with no check value
5.  with a bogus key/value
6.  with a check that isn't in the paramOptions
7.  with an output that isn't in the paramOptions

CHECK ALL FIELDS
8. check=all. A test that gets back an element from each field - special. Gets back the whole doc

CHECK EXISTS
9. output=exists. A test that just returns a true or false. Expects back {"exists":true} 

CHECK THE OUTPUT
10. output=all for any check/token combo. A test that returns a list of docs.
11. output=pho for any check/token combo. A test that returns a list of phonetics that matched a word
12. output=word for any check/token combo. A test that returns a list of words that matched a phonetic


--post-buffering
--pep333-input --post-buffering 4096 to uwsgi

'''

import unittest
import urllib2
import os
import sys
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
import json
    
#---------------------------------------------------------------------------

class Test(unittest.TestCase):

    def setUp(self):
        ''' sets up parameters before each test'''
        
        # The base url to hit
        self.url = 'http://localhost:8044'

        # Config information from a relative path
        configPath = os.path.join(wsDir, 'config')
        configFile = 'testsWordslang.cfg'
        self.p = getConfigParameters(os.path.join(configPath, configFile))
        
        self.c, dbh, collection, emoCollection = getMongoHandles(self.p)

        # Build a document and insert it 
        doc1 = {"pho" : "sml",
                 "slang" : ["smlie", "smiiile", "2smile", "smiiileee", "smilee",
                            "usmile", "smilie", "simle", "smillleee", "smillle",
                            "smille", "smileee", "*s*", "smle", "smilert", "smiile",
                            "smil", "smie", ": )", "(-:"],
                 "word" : "smile"}
        
        doc2 = {"pho" : "st",
                 "slang" : [ "sosad", "ssad", "saaad", "saaddd",
                        "saaadd", "sadd", "saadd", "saddd",
                        "saddy", "saad", "saaaddd", ": (", ": ["],
                "word" : "sad"}
        
        doc3 = {"pho" : "unh",
                 "slang" : [ "sad"],
                "word" : "unhappy"}

                
        # Insert a couple of documents
        id1 = collection.insert(doc1) 
        id2 = collection.insert(doc2)
        id3 = collection.insert(doc3)
        self.document1 = doc1
        self.document2 = doc2
        self.document3 = doc3
        
        # Documents to go into the emoticons collection
        doc4 = {"word" : "smile",
                "emo"  : [":-)"]}
        id4 = emoCollection.insert(doc4)
        self.document4 = doc4
        
#---------------------------------------------------------------------------
    def tearDown(self):
        '''Tearsdown after each test'''
        
        # Drop the db
        self.c.drop_database(self.p.db)
        # CLose the connection
        self.c.disconnect()
    
#---------------------------------------------------------------------------
    def testBasicCheck(self):
        '''Checks a basic /test GET request'''
        
        truth = '{"hello": "foobar"}'
        jsonTruth = {'hello':'foobar'}
        
        response = urllib2.urlopen(self.url + '/test')
        out = response.read()
        jsonOut = json.loads(out)
        
        self.assertEquals(truth, out)
        self.assertEquals(jsonTruth, jsonOut)
        
#---------------------------------------------------------------------------
    def testNoToken(self):
        ''' Test involving no token provided'''
        
        try:
            url = '%s/wordslang?' %(self.url)
            response = urllib2.urlopen(url)
            x = 'sucess'
        except:
            x = 'failed'
        self.assertEquals(x, 'failed')

#---------------------------------------------------------------------------
    def testNoCheck(self):
        ''' Test involving no check provided'''
        
        try:
            url = '%s/wordslang?%s' %(self.url, 'token=smile')
            response = urllib2.urlopen(url)
            x = 'sucess'
        except urllib2.HTTPError:
            x = 'failed'
        
        self.assertEquals(x,'failed')
            
#---------------------------------------------------------------------------
    def testNoOutput(self):
        ''' Test involving no check provided'''
        
        try:
            url = '%s/wordslang?%s&%s' %(self.url,
                                         'token=smile',
                                         'check=word')
            response = urllib2.urlopen(url)
            x = 'sucess'
        except urllib2.HTTPError:
            x = 'failed'
        
        self.assertEquals(x, 'failed')
            
#---------------------------------------------------------------------------
    def testAll3(self):
        ''' Test involving all 3 being present. '''
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,
                                     'token=smile',
                                     'check=word',
                                     'output=exists')
        response = urllib2.urlopen(url)
        out = response.read()
        
        truth     = '{"exists": "true"}'
        truthJson = json.loads(truth)
        
        self.assertEquals(out, truth)
        self.assertEquals(truthJson, json.loads(out))

#---------------------------------------------------------------------------
    def testInvalidCheck(self):
        ''' Test an invalid check value '''
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=smile', 'check=rubbish','output=exists')
        try:
            out = urllib2.urlopen(url).read()
            x = 'sucess'
        except urllib2.HTTPError:
            x = 'failed'
        
        self.assertEquals(x, 'failed')

#---------------------------------------------------------------------------
    def testCheckAll(self):
        '''  Check=all and exists - says whether it exists in 1 or more fields. '''

        # The truth values
        truth     = '{"exists": "true"}'
        truthJson = json.loads(truth)
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=smile', 'check=all','output=exists')
        out = urllib2.urlopen(url).read()

        self.assertEquals(truth, out)
        self.assertEquals(truthJson, json.loads(out))

#---------------------------------------------------------------------------
    def testCheckAllOutputAll(self):
        '''  Check=all and output=all - returns the complete document. '''
        
        doc1 = [{"pho" : "sml",
                 "slang" : ["smlie", "smiiile", "2smile", "smiiileee", "smilee",
                            "usmile", "smilie", "simle", "smillleee", "smillle",
                            "smille", "smileee", "*s*", "smle", "smilert", "smiile",
                            "smil", "smie", ": )", "(-:"],
                 "word" : "smile"}]
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=smile', 'check=all','output=all')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(doc1, json.loads(outRes))

#---------------------------------------------------------------------------
    def testCheckAllOutputAllAsList(self):
        '''  Check=all and output=all - returns the complete document. '''

        doc2 = {"pho" : "st",
                 "slang" : [ "sosad", "ssad", "saaad", "saaddd",
                        "saaadd", "sadd", "saadd", "saddd",
                        "saddy", "saad", "saaaddd", ": (", ": ["],
                "word" : "sad"}
        
        doc3 = {"pho" : "unh",
                 "slang" : [ "sad"],
                "word" : "unhappy"}
        
        docTest = [doc2, doc3]

        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=sad', 'check=all','output=all')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(docTest, json.loads(outRes))
        
#---------------------------------------------------------------------------
    def testCheckAllOutputPho(self):
        '''  Check=all and output=pho - returns a list of phonetics. '''

        phoOnly = [{"pho" : "st"},{"pho" : "unh"}]
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=sad', 'check=all','output=pho')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(phoOnly, json.loads(outRes))
        
#---------------------------------------------------------------------------
    def testCheckWordOutputExists(self):
        '''  Check=all and output=exists - returns an exist statement. '''

        phoOnly = {"exists" : "true"}
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=sad', 'check=word','output=exists')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(phoOnly, json.loads(outRes))

#---------------------------------------------------------------------------
    def testCheckWordOutputAll(self):
        '''  Check=word and output=all - returns the complete document. '''

        doc2 = [{"pho" : "st",
                 "slang" : [ "sosad", "ssad", "saaad", "saaddd",
                        "saaadd", "sadd", "saadd", "saddd",
                        "saddy", "saad", "saaaddd", ": (", ": ["],
                "word" : "sad"}]
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=sad', 'check=word', 'output=all')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(doc2, json.loads(outRes))

#---------------------------------------------------------------------------
    def testCheckWordOutputPho(self):
        '''  Check=word and output=pho - returns just the phonetic. '''

        phoOnly = [{"pho" : "st"}]
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=sad', 'check=word', 'output=pho')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(phoOnly, json.loads(outRes))
    
#---------------------------------------------------------------------------
    def testCheckPhoOutputWord(self):
        '''  Check=pho and output=word - returns just the words. '''

        phoOnly = [{"word" : "sad"}]
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=ST', 'check=pho', 'output=word')
        outRes = urllib2.urlopen(url).read()
        self.assertEquals(phoOnly, json.loads(outRes))

#---------------------------------------------------------------------------
    def testCheckPUT(self):
        '''  Check to see whether PUT is successful'''
        
        urlIn = self.url+'/putslang'
        print urlIn
        
        x = 0
        updateJson = [{"word" : "sad", "slang": "yooo"}]
        jsonPayload = json.dumps(updateJson)
        
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(urlIn, data=jsonPayload)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
        url = opener.open(request)
        print url.read()
        
        if x == 0:
            print x
        #self.assertEquals(updateJson, json.loads(outRes))
#---------------------------------------------------------------------------
    def testEmo1(self):
        '''Checks a basic /test GET request'''
        
        truth = '[{"word": "smile"}]'
        jsonTruth = json.loads(truth)
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=:-)', 'check=emo', 'output=word')
        out = urllib2.urlopen(url).read()
        jsonOut = json.loads(out)
        
        self.assertEquals(truth, out)
        self.assertEquals(jsonTruth, jsonOut)

#---------------------------------------------------------------------------
    def testEmo2(self):
        '''Checks a basic /test GET request - exists'''
        
        truth = '{"exists": "true"}'
        jsonTruth = json.loads(truth)
        
        url = '%s/wordslang?%s&%s&%s' %(self.url,'token=:-)', 'check=emo', 'output=exists')
        out = urllib2.urlopen(url).read()
        jsonOut = json.loads(out)
        
        self.assertEquals(truth, out)
        self.assertEquals(jsonTruth, jsonOut)
    
#---------------------------------------------------------------------------
    def testRegex(self):
        '''Checks the regex functionality.'''
        
        truth = '{"exists": "true"}'
        jsonTruth = json.loads(truth)
        
        url = '%s/wordslang?%s&%s&%s&%s' %(self.url,'token=miler', 'check=slang', 'output=exists', 'regex=true')
        out = urllib2.urlopen(url).read()
        jsonOut = json.loads(out)
        
        self.assertEquals(truth, out)
        self.assertEquals(jsonTruth, jsonOut)
        
        
#---------------------------------------------------------------------------


if __name__ == "__main__":
    
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()    

