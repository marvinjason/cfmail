from constants import COUNTRIES, MESSAGE_CATEGORIES as CATEGORIES, SEXES
from datetime import datetime
from google.appengine.ext import ndb
from pybcrypt import bcrypt
from uuid import getnode, uuid4
import time

class User(ndb.Model):

	username = ndb.StringProperty(required=True)
	email = ndb.ComputedProperty(lambda self: self.username + '@cfmail.com')
	password = ndb.StringProperty(required=True)
	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	datetime_updated = ndb.DateTimeProperty(auto_now=True)
	first_name = ndb.StringProperty(required=True)
	middle_name = ndb.StringProperty(required=True)
	last_name = ndb.StringProperty(required=True)
	sex = ndb.StringProperty(required=True, choices=SEXES)
	birthdate = ndb.DateProperty(required=True)
	age = ndb.ComputedProperty(lambda self: datetime.now().year - self.birthdate.year - 
							   ((datetime.now().month, datetime.now().day) < (self.birthdate.month, self.birthdate.day)))
	contact_number = ndb.StringProperty()
	address = ndb.StringProperty(required=True)
	postal_code = ndb.StringProperty(required=True)
	country = ndb.StringProperty(required=True, choices=COUNTRIES)

	@classmethod
	def make_key(cls, id):
		return ndb.Key(cls, id)

	@classmethod
	def exists(cls, username):
		return cls.query(cls.username == username).count() > 0

	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'username': self.username,
			'email': self.email,
			'password': self.password,
			'datetime_created': self.datetime_created,
			'datetime_updated': self.datetime_updated,
			'first_name': self.first_name,
			'middle_name': self.middle_name,
			'last_name': self.last_name,
			'sex': self.sex,
			'birthdate': self.birthdate,
			'age': self.age,
			'contact_number': self.contact_number,
			'address': self.address,
			'postal_code': self.postal_code,
			'country': self.country
		}

		if include != None and exclude != None:
			raise KeyError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}

# End of class User

class Message(ndb.Model):

	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	from_recipient = ndb.KeyProperty(kind='User')
	subject = ndb.StringProperty()
	body = ndb.StringProperty()

	def serialize(self, include=None, exclude=None):
		pointers = list(MessagePointer.query(MessagePointer.message == self.key).fetch())
		serialized = {
			'id': self.key.id(),
			'datetime_created': self.datetime_created,
			'from_recipient': self.from_recipient.get().email,
			'sender': self.from_recipient.get().serialize(include=['id', 'email',
																   'first_name', 'middle_name',
																   'last_name']),
			'to_recipient': [p.to_recipient.get().email for p in pointers],
			'recipients': [p.to_recipient.get().serialize(include=['id', 'email',
																   'first_name', 'middle_name',
																   'last_name']) for p in pointers],
			'subject': self.subject,
			'body': self.body
		}

		if include != None and exclude != None:
			raise KeyError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}

# End of class Message

class MessagePointer(ndb.Model):

	message = ndb.KeyProperty(kind='Message')
	datetime_updated = ndb.DateTimeProperty(auto_now=True)
	to_recipient = ndb.KeyProperty(kind='User')
	category = ndb.StringProperty(default=CATEGORIES[0], choices=CATEGORIES)
	is_read = ndb.BooleanProperty(default=False)

	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'message': self.message.id(),
			'datetime_updated': self.datetime_updated,
			'timestamp': time.mktime(self.datetime_updated.timetuple()),
			'category': self.category,
			'is_read': self.is_read
		}

		serialized.update(self.message.get().serialize(exclude=['id']))

		if include != None and exclude != None:
			raise KeyError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}

# End of class MessagePointer

class Session(ndb.Model):

	access_token = ndb.StringProperty(required=True)
	user = ndb.KeyProperty(kind='User')
	mac_address = ndb.IntegerProperty(required=True)
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now_add=True)

	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'access_token': self.access_token,
			'user': self.user.id(),
			'mac_address': self.mac_address,
			'datetime_created': self.date_created,
			'datetime_updated': self.date_updated
		}

		if include != None and exclude != None:
			raise KeyError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}

# End of class Session