#User class 
from google.appengine.ext import ndb
from dictionary import Dictionary 

class MyUser(ndb.Model):
	userDictionary = ndb.StringProperty(repeated=True)
	wordCount = ndb.IntegerProperty()

