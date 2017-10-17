from datetime import datetime
from google.appengine.ext import ndb
from pycountry import countries
from uuid import uuid4


class User(ndb.Model):

	SEXES = ('male', 'female')
	COUNTRIES = tuple([c.name for c in list(countries)])

	@classmethod
	def make_key(cls, id):
		return ndb.Key(cls, id)

	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	datetime_updated = ndb.DateTimeProperty(auto_now_add=True)
	username = ndb.StringProperty(required=True)
	email = ndb.ComputedProperty(lambda self: self.username + '@cfmail.com')
	password = ndb.StringProperty(required=True)
	first_name = ndb.StringProperty(required=True)
	middle_name = ndb.StringProperty(required=True)
	last_name = ndb.StringProperty(required=True)
	sex = ndb.StringProperty(required=True, choices=SEXES)
	birthdate = ndb.DateTimeProperty(required=True)
	age = ndb.ComputedProperty(lambda self: datetime.now().year - self.birthdate.year - ((datetime.now().month, datetime.now().day) < (self.birthdate.month, self.birthdate.day)))
	contact_number = ndb.StringProperty()
	address = ndb.StringProperty(required=True)
	postal_code = ndb.StringProperty(required=True)
	country = ndb.StringProperty(required=True, choices=COUNTRIES)
	
	
class Message(ndb.Model):

	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	from_recipient = ndb.KeyProperty(kind='User')
	subject = ndb.StringProperty()
	body = ndb.StringProperty()
	
	
class MessageReceipt(ndb.Model):

	CATEGORIES = ('drafts', 'inbox', 'trash')
	
	message_id = ndb.KeyProperty(kind='Message')
	datetime_updated = ndb.DateTimeProperty(auto_now_add=True)
	to_recipient = ndb.KeyProperty(kind='User')
	category = ndb.StringProperty(default=CATEGORIES[0], choices=CATEGORIES)
	seen_status = ndb.BooleanProperty(default=False)


class Session(ndb.Model):

	access_token = ndb.ComputedProperty(lambda self: str(uuid4()))
	user = ndb.KeyProperty(kind='User')
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)