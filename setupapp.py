import sys
import configureDatabase
import setupDatabase
import insertEnglishDictionary as ied
import insertEnglishSlang as ies
import insertEmoticons as ie

# Get the config file
configFile = sys.argv[1]

# Configuring the dotcloud settings for mongodb
print 'Configuring the dotcloud settings for mongodb'
configureDatabase.main(configFile)

# Setup the database
print 'Setting up and populating database'
setupDatabase.main(configFile)

# Insert the large english dictionary
print 'Inserting main english dictionary'
ied.main(configFile)

# Insert the normalised file database
print 'Inserting normalised english list'
ies.main(configFile, file='norm')

# Insert the slang database
print 'Inserting slang list'
ies.main(configFile, file='slang')

# Insert the emoticons
print 'Inserting emoticons'
ie.main(configFile)

# Called using:
#python setupapp.py ~/Documents/Code/eclipseWorkspace/wordslang/config/wordslang.cfg
