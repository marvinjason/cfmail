from google.appengine.ext import ndb

class User(ndb.Model):
	last_name = ndb.StringProperty(required=True)
	first_name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)
