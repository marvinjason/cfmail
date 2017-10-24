# Imports:
from google.appengine.ext import ndb
from user_model import User
from uuid import uuid4

# Session Model:
class Session(ndb.Model):

	# Attributes:
	access_token = ndb.StringProperty(required=True)
	user_key = ndb.KeyProperty(kind='User')
	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	datetime_updated = ndb.DateTimeProperty(auto_now=True)


	@classmethod
	def make_access_token(cls):
		return str(uuid4())


	@classmethod
	def authenticate(cls, user_id, access_token):
		user_key = User.make_key(user_id)

		if not user_key:
			return False

		session = cls.query(ndb.AND(cls.access_token == access_token,
                                    cls.user_key == user_key)).get()
		return session if session else False


	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'access_token': self.access_token,
			'user_key': self.user_key.id(),
			'datetime_created': self.datetime_created,
			'datetime_updated': self.datetime_updated
		}

		if include != None and exclude != None:
			raise ValueError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}