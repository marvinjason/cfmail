# Imports:
from ..constants import COUNTRIES, SEXES
from datetime import datetime
from google.appengine.ext import ndb
from pybcrypt import bcrypt

# User Model:
class User(ndb.Model):

	# Attributes:
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
                              ((datetime.now().month, datetime.now().day) <
                              (self.birthdate.month, self.birthdate.day)))
	contact_number = ndb.StringProperty()
	address = ndb.StringProperty(required=True)
	postal_code = ndb.StringProperty(required=True)
	country = ndb.StringProperty(required=True, choices=COUNTRIES)


	@classmethod
	def make_key(cls, id):
		id = long(id)
		return ndb.Key(cls, id) if cls.get_by_id(id) else False


	@classmethod
	def exist_username(cls, username):
		return cls.query(cls.username == username).count() > 0


	@classmethod
	def encrypt_password(cls, password):
		return bcrypt.hashpw(password, bcrypt.gensalt())


	def equal_password(self, input_password):
		return bcrypt.hashpw(input_password, self.password) == self.password


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
			raise ValueError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}