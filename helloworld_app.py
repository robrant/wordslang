from bottle import route
import os

htdocs = '%s/pub' % os.getcwd()

x = 1

@route('/hello')
def hello():
        
        return 'Hello world %s' %x
