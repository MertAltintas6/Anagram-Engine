import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os

from myuser import MyUser
from dictionary import Dictionary

JINJA_ENVIRONMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True)

class SubAnagram(webapp2.RequestHandler):
	def orderLetters(self, word):
		key = "".join(sorted(word))
		return key

	def getSubkeys(self,key,index,keys):
		orderedKey = self.orderLetters(key)
		if(index < 0):
			return keys
		else:
			letters = list(orderedKey)
			letters.remove(orderedKey[index])
			new_key = "".join(letters)
			if new_key not in keys:
				keys.append(new_key)
			index -=1
			self.getSubkeys(orderedKey,index,keys)
			return keys

	def getAllSubKeys(self,key,keys):
		allSubKeys = self.getSubkeys(key, len(key)-1,keys)
		for key in allSubKeys:
			if len(key) > 3:
				self.getSubkeys(key,len(key)-1,keys)
		return keys


	def get(self):
		self.response.headers['Content-Type'] = 'text/html'

		user = users.get_current_user()		
		myuser = None

		if user == None:
			template_values = {'login_url':users.create_login_url(self.request.uri)}
			template = JINJA_ENVIRONMENT.get_template('mainpage_guest.html')
			self.response.write(template.render(template_values))
			return

		else:
			myuser_key = ndb.Key('MyUser', user.user_id())
			myuser = myuser_key.get()

			if myuser == None:
				myuser = MyUser(id=user.user_id(), wordCount=0)
				myuser.put()

			template_values = {'logout_url':users.create_logout_url(self.request.uri),'myuser': myuser,'myuserAnagrams':len(myuser.userDictionary)}
			template = JINJA_ENVIRONMENT.get_template('subanagram.html')
			self.response.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()
		
		myuser_key = ndb.Key('MyUser', user.user_id())
		myuser = myuser_key.get()
		
		button = self.request.get("button")
		
		if button == "Enter":
			text = self.request.get('anagram_text').strip()
			keys = []
			self.getAllSubKeys(text,keys)
			dictionaries = []
			for key in keys:
				newKey = user.user_id()+":"+key
				if newKey in myuser.userDictionary:
					dictionary_key = ndb.Key('Dictionary',newKey)
					dictionary = dictionary_key.get()
					dictionaries.append(dictionary.wordList)

			if len(dictionaries) <1:
				self.redirect('/subanagram')
				return
			
			template_values = {'logout_url':users.create_logout_url(self.request.uri), 'dictionaries': dictionaries, 'text':text,'myuser': myuser,'myuserAnagrams':len(myuser.userDictionary)}
			template = JINJA_ENVIRONMENT.get_template('subanagram.html')
			self.response.write(template.render(template_values))
