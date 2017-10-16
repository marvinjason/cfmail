from google.appengine.ext import ndb

class User(ndb.Model):
	last_name = ndb.StringProperty(required=True)
	first_name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)

class Message(ndb.Model):
	subject = ndb.StringProperty()
	body = ndb.TextProperty()
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)
	user = ndb.KeyProperty(kind='User')
	category = ndb.KeyProperty(kind='Category')

class MessageReceipt(ndb.Model):
	user = ndb.KeyProperty(kind='User')
	message = ndb.KeyProperty(kind='Message')
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)

class Category(ndb.Model):
	title = ndb.StringProperty(required=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)