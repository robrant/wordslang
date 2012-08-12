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

import configureDatabase
import setupDatabase
import insertEnglishDictionary as ied
import insertEnglishSlang as ies
import insertEmoticons as ie

# Get the config file
configFile = sys.argv[1]

# Where this is being run - 
site = sys.argv[2]

# Configuring the dotcloud settings for mongodb
if site == 'dotcloud':
    print 'Configuring the dotcloud settings for mongodb'
    configureDatabase.main(configFile)
elif site == 'local':
    print 'Skipping all dotcloud configuration. '
    pass

# Setup the database
print 'Setting up and populating database'
setupDatabase.main(configFile)

# Insert the large english dictionary
print 'Inserting main english dictionary'
#ied.main(configFile)

# Insert the normalised file database
print 'Inserting normalised english list'
#ies.main(configFile, file='norm')

# Insert the slang database
print 'Inserting slang list'
#ies.main(configFile, file='slang')

# Insert the emoticons
print 'Inserting emoticons'
#ie.main(configFile)

# Called using:
#python setupapp.py ~/Documents/Code/eclipseWorkspace/wordslang/config/wordslang.cfg
