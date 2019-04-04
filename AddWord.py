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


class AddWord(webapp2.RequestHandler):
	def orderLetters(self, word):
		key = "".join(sorted(word))
		return key


	def addWord(self, key, myuser, word):
		dictionary_key = ndb.Key('Dictionary', key)
		dictionary = dictionary_key.get() 
		fail = True
		if dictionary == None:
			w_list = []
			keyList = []
			dictionary = Dictionary(wordList = w_list, wordCount= len(w_list), letterCount = len(key.split(":")[-1]), subanagramKeys=keyList)
			dictionary.key = ndb.Key('Dictionary', key)
			dictionary.put()

		if word not in dictionary.wordList:
			dictionary.wordList.append(word)
			dictionary.wordCount = len(dictionary.wordList)
			myuser.wordCount+=1
			dictionary.put()
			myuser.put()
			fail = False
		if key not in myuser.userDictionary:
			myuser.userDictionary.append(key)
			myuser.put()

		return fail


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
				myuser = MyUser(id=user.user_id())
				myuser.put()


			template_values = {'logout_url':users.create_logout_url(self.request.uri), 'myuser': myuser, 'myuserAnagrams':len(myuser.userDictionary), 'fail':False}
			template = JINJA_ENVIRONMENT.get_template('add.html')
			self.response.write(template.render(template_values))


	def post(self):

		button = self.request.get("button")
		user = users.get_current_user()
		
		myuser_key = ndb.Key('MyUser', user.user_id())
		myuser = myuser_key.get()
		

		if button == "Add Word":
			word = self.request.get("word").strip()

			key = user.user_id()+":"+self.orderLetters(word) 

			fail = self.addWord(key,myuser,word)

			template_values = {'logout_url':users.create_logout_url(self.request.uri), 'myuser': myuser, 'myuserAnagrams':len(myuser.userDictionary), 'fail':fail, 'text':word}
			template = JINJA_ENVIRONMENT.get_template('add.html')
			self.response.write(template.render(template_values))
			return

		elif button == "Submit":
			file = self.request.get('txtFile')
			path = os.path.dirname(os.path.abspath(__file__))
			f = open(path+'/'+file,'r')
			for word in f:
				word = word.split('\n')[0]
				key = user.user_id()+":"+self.orderLetters(word) 
				self.addWord(key,myuser,word)

			
		self.redirect('/add')