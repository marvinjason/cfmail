# Imports:
from google.appengine.ext import ndb

# Message Model:
class Message(ndb.Model):

    # Attributes:
	datetime_created = ndb.DateTimeProperty(auto_now_add=True)
	datetime_updated = ndb.DateTimeProperty(auto_now=True)
	from_recipient = ndb.KeyProperty(kind='User')
	to_recipients = ndb.KeyProperty(kind='User', repeated=True)
	subject = ndb.StringProperty()
	body = ndb.StringProperty()


	def serialize(self, include=None, exclude=None):
		serialized = {
			'id': self.key.id(),
			'datetime_created': self.datetime_created,
			'datetime_updated': self.datetime_updated,
			'from_recipient': self.from_recipient.id(),
			'to_recipients': [k.id() for k in self.to_recipients],
			'subject': self.subject,
			'body': self.body
		}

		if include != None and exclude != None:
			raise ValueError("Cannot use both 'include' and 'exclude'.")

		return {k: v for k, v in serialized.iteritems()
				if (include == None and exclude == None)
				or (exclude == None and k in include)
				or (include == None and k not in exclude)}