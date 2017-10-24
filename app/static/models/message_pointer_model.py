# Imports:
from ..constants import MESSAGE_CATEGORIES as CATEGORIES, MESSENGER_ROLES as ROLES
from google.appengine.ext import ndb

# Message Pointer Model
class MessagePointer(ndb.Model):

	# Attributes:
	message_key = ndb.KeyProperty(kind='Message', required=True)
	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	datetime_updated = ndb.DateTimeProperty(auto_now=True)
	role = ndb.StringProperty(choices=ROLES, required=True)
	recipient = ndb.KeyProperty(kind='User', required=True)
	category = ndb.StringProperty(default=CATEGORIES[2], choices=CATEGORIES)
	is_read = ndb.BooleanProperty(default=False)


	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'message_key': self.message_key.id(),
			'datetime_created': self.datetime_created,
			'datetime_updated': self.datetime_updated,
			'role': self.role,
            'recipient': self.recipient.id(),
			'category': self.category,
			'is_read': self.is_read
		}

		if include != None and exclude != None:
			raise KeyError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}