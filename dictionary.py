#Dictionary class 
from google.appengine.ext import ndb

class Dictionary(ndb.Model):
	wordList = ndb.StringProperty(repeated=True)
	wordCount = ndb.IntegerProperty()
	letterCount = ndb.IntegerProperty()
	subanagramKeys = ndb.StringProperty(repeated=True)
