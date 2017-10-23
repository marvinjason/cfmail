from constants import MESSAGE_CATEGORIES as CATEGORIES, get_status_code
from datetime import datetime
from flask import Blueprint, jsonify, request
from google.appengine.ext import ndb
from models import Message, MessagePointer, Session, User
from pybcrypt import bcrypt
from uuid import getnode as get_mac, uuid4

def authenticate():
    access_token = request.args.get('access_token')
    session = Session.query(Session.access_token == access_token).get() if access_token else None
        
    return session if session else False

# Users Controller
users = Blueprint('users', __name__)

@users.route('/users')
def index():
    try:
	    return 'user'

    except Exception as e:
        return get_status_code(401)
# End of def index

@users.route('/users', methods=['POST'])
def create():
    try:
        data = request.get_json()

        if User.exists(data['username']):
            raise KeyError("Username '{0}' already exist.".format(data['username']))
        
        user = User()
        
        for k, v in data.iteritems():
            v = (bcrypt.hashpw(v, bcrypt.gensalt()) if k == 'password'
                else datetime.strptime(v, '%Y-%m-%d').date() if k == 'birthdate'
                else v)

            exec("user.{0} = v".format(k))

        user.put()
        return jsonify(user.serialize(exclude=['password']))

    except Exception as e:
        return get_status_code(400)
# End of def create

@users.route('/users/<id>', methods=['GET'])
def show(id):
    try:
        user = User.get_by_id(int(id))

        return jsonify(
            user.serialize() if authenticate()
            else user.serialize(include=['id', 'username', 'email', 'first_name', 'middle_name', 'last_name'])
        )

    except Exception as e:
        return get_status_code(401)
# End of def show

@users.route('/users/<id>', methods=['PUT'])
def update(id):
    try:
        session = authenticate()

        if session.user.id() != int(id):
            raise KeyError()

        data = request.get_json()
        user = session.user.get()
        updates = ['username', 'email']
        
        for k, v in data.iteritems():
            if k in ['username', 'email', 'birthdate' 'age',
                    'datetime_created', 'datetime_udpated']:
                continue

            v = (bcrypt.hashpw(v, bcrypt.gensalt()) if k == 'password' else v)
            exec("user.{0} = v".format(k))
            updates.append(k)

        user.put()
        return jsonify(user.serialize(include=updates))

    except Exception as e:
        return get_status_code(401)
# End of def update

@users.route('/users/<id>', methods=['DELETE'])
def destroy(id):
    try:
        session = authenticate()

        if session.user.id() != int(id):
            raise KeyError()

        user = session.user.get()
        response = user.serialize()
        user.key.delete()
            
        return jsonify(response)

    except Exception as e:
        return get_status_code(401)

# End of Users Controller

# Sessions Controller
sessions = Blueprint('sessions', __name__)

@sessions.route('/sessions', methods=['POST'])
def create():
    try:
        data = request.get_json()
        email = (data['email'] if data['email']
                 else data['username'] if data['username']
                 else None)
        password = data['password']
        user = User.query(ndb.OR(User.email == email, User.username == email)).get()
        session = (Session(user=user.key)
                   if user and bcrypt.hashpw(password, user.password) == user.password
                   else None)
        
        if user and bcrypt.hashpw(password, user.password) == user.password:
            session = Session(
                user=user.key,
                access_token=str(uuid4()),
                mac_address=get_mac())

            session.put()
            
        return jsonify(session.serialize(exclude=['datetime_updated', 'mac_address', 'id']))

    except Exception as e:
        return get_status_code(401)
# End of def create

@sessions.route('/sessions', methods=['DELETE'])
def destroy():
    try:
        session = authenticate()
        response = session.serialize()
        session.key.delete()

        return jsonify(response)

    except Exception as e:
        return get_status_code(401)
# End of def destroy

# End of Sessions Controller

# Messages Controller
messages = Blueprint('messages', __name__)

@messages.route('/users/<id>/messages', methods=['GET'])
def index(id):
    try:
        session = authenticate()

        if session.user.id() != long(id):
            return get_status_code(401)

        user = session.user.get()
        args = request.args
        filter = args.get('filter', CATEGORIES[0])
        page = args.get('page', '1')
        count = int(args.get('count', 20))
        offset = (int(page) - 1) * count
        data = []
        total_count = 0

        if filter in CATEGORIES[:2]:
            data = MessagePointer.query(ndb.AND(MessagePointer.to_recipient == session.user, MessagePointer.category == filter)).order(-MessagePointer.datetime_created).fetch(count, offset=offset)
            total_count = MessagePointer.query(MessagePointer.to_recipient == session.user).count()

        elif filter in CATEGORIES[2:]:
            messages = Message.query(Message.from_recipient == session.user).order(-Message.datetime_created).fetch(count, offset=offset)
            
            for m in messages:
                pointer = MessagePointer.query(ndb.AND(MessagePointer.message == m.key, MessagePointer.category == filter)).get()
                data += [pointer] if pointer else []

            messages = Message.query(Message.from_recipient == session.user).fetch()
            
            for m in messages:
                pointer = MessagePointer.query(ndb.AND(MessagePointer.message == m.key, MessagePointer.category == filter)).get()
                total_count += 1 if pointer else 0

        else:
            return get_status_code(400)

        response = {
            'filter': filter,
            'total_count': total_count,
            'messages': [m.serialize(include=['id', 'body', 'is_read', 'sender', 'subject', 'timestamp']) for m in data]
        }
        
        return jsonify(response)

    except Exception as e:
        return str(e)#get_status_code(401)
# End of def index

@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['GET'])
def show(user_id, pointer_id):

    try:
        session = authenticate()

        if session.user.id() != long(user_id):
            raise KeyError()

        pointer = MessagePointer.get_by_id(long(pointer_id))
        pointer.is_read = True
        pointer.put()

        return jsonify(pointer.serialize(exclude=['datetime_created', 'datetime_updated', 'from_recipient', 'message', 'to_recipient']))

    except Exception as e:
        return get_status_code(404)
# End of def show

@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['PUT'])
def update(user_id, pointer_id):
    try:
        session = authenticate()

        if not session:
            return get_status_code(403)

        if session.user.id() != long(user_id):
            return get_status_code(401)

        data = request.get_json()
        pointer = ndb.Key('MessagePointer', long(pointer_id)).get()

        if not pointer:
            return get_status_code(404)

        if 'is_read' in data:
            pointer.is_read = data['is_read']
            
        if 'category' in data:
            pointer.category = data['category']

        pointer.put()

        return jsonify(pointer.serialize())
    except Exception as e:
        return str(e)#get_status_code(401)


@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['DELETE'])
def destroy(user_id, pointer_id):
    try:
        session = authenticate()

        if session and session.user.id() == long(user_id):
            pointer = MessagePointer.get_by_id(long(pointer_id))
            if not pointer:
                return get_status_code(400)

            pointer.key.delete()
            return jsonify(pointer.serialize(exclude=['datetime_created', 'datetime_updated', 'from_recipient', 'message', 'to_recipient']))
        else:
            return get_status_code(401)
    except Exception as e:
        return get_status_code(404)


@messages.route('/users/<id>/messages', methods=['POST'])
def create(id):
    # JSON:
    #     {
    #         "subject": "My Subject",
    #         "body": "My Body",
    #         "recipients": [
    #             "email1@cfmail.com",
    #             "email2@cfmail.com",
    #             "email3@cfmail.com"
    #         ]
    #     }
    try:
        session = authenticate()
        
        if session and session.user.id() == long(id):
            data = request.get_json()
            
            message = Message(
                subject=data['subject'],
                body=data['body'],
                from_recipient=session.user
            )
            message.put()

            message_recipients = []

            for recipient in data['recipients']:
                user = User.query(User.email == recipient).get()
                if user:
                    message_recipients.append(
                        MessagePointer(
                            message=message.key,
                            category=CATEGORIES[2],
                            to_recipient=user.key
                        ).put()
                    )

            response = {
                'id': message.key.id(),
                'subject': message.subject,
                'body': message.body,
                'recipients': [
                        {
                            'id': i.get().to_recipient.id(),
                            'email': i.get().to_recipient.get().email
                        } for i in message_recipients
                    ],
                'timestamp': message.datetime_created
            }
            
            return jsonify(response)

    except Exception as e:
        return str(e) #get_status_code(400)

# End of Messages Controller