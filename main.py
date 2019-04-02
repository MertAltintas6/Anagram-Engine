import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os

from myuser import MyUser
from dictionary import Dictionary
from AddWord import AddWord
from subanagram import SubAnagram

JINJA_ENVIRONMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True)

class MainPage(webapp2.RequestHandler):
	
	def orderLetters(self, word):
		key = "".join(sorted(word))
		return key


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

			template_values = {'logout_url':users.create_logout_url(self.request.uri),'myuserAnagrams':len(myuser.userDictionary), 'myuser':myuser}
			template = JINJA_ENVIRONMENT.get_template('mainpage.html')
			self.response.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()
		
		myuser_key = ndb.Key('MyUser', user.user_id())
		myuser = myuser_key.get()
		
		button = self.request.get("button")
		
		dictionaries = []
		keys = []
		
		if button == "Enter":
			text = self.request.get("user_text")
			words = text.split()
			for word in words:
				key = user.user_id()+":"+self.orderLetters(word)
				if key not in keys:
					keys.append(key)
					if key in myuser.userDictionary:
						dictionary_key = ndb.Key('Dictionary',key)
						dictionary = dictionary_key.get()
						dictionaries.append(dictionary.wordList)
			
			if len(dictionaries) <1:
				self.redirect('/')
				return
			
			template_values = {'logout_url':users.create_logout_url(self.request.uri), 'dictionaries': dictionaries, 'text':text, 'myuserAnagrams':len(myuser.userDictionary),'myuser':myuser}
			template = JINJA_ENVIRONMENT.get_template('mainpage.html')
			self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/add',AddWord),
	('/subanagram', SubAnagram)], debug = True)