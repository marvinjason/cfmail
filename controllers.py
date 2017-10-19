from constants import get_status_code
from datetime import datetime
from flask import Blueprint, jsonify, request
from google.appengine.ext import ndb
from models import Message, MessageReceipt, Session, User
from pybcrypt import bcrypt
from uuid import getnode as get_mac


def is_authenticated():
    access_token = request.args.get('access_token')
    session = None
    
    if access_token:
        session = Session.query(Session.access_token == access_token).get()
        
    return session if session else False


users = Blueprint('users', __name__)


@users.route('/users')
def index():
    try:
	    return 'user'

    except Exception as e:
        return get_status_code(401)
    

@users.route('/users', methods=['POST'])
def create():
    try:
        data = request.get_json()

        if User.exists(data['username']):
            return get_status_code(400)
        
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


@users.route('/users/<id>', methods=['GET'])
def show(id):
    try:
        user = User.get_by_id(int(id))
        return jsonify(user.serialize())

    except Exception as e:
        return get_status_code(401)

@users.route('/users/<id>', methods=['PUT'])
def update(id):
    try:
        session = is_authenticated()

        if session.user.id() == int(id):
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


@users.route('/users/<id>', methods=['DELETE'])
def destroy(id):
    session = is_authenticated()

    try:
        if session.user.id() == int(id):
            user = session.user.get()
            response = user.serialize()
            user.key.delete()
            
        return jsonify(response)

    except Exception as e:
        return get_status_code(401)


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
            session = Session(user=user.key)
            session.put()
            
        return jsonify(session.serialize(exclude=['datetime_updated', 'mac_address', 'id']))

    except Exception as e:
        return get_status_code(401)


@sessions.route('/sessions', methods=['DELETE'])
def destroy():
    try:
        session = is_authenticated()

        if session:
            user = session.user.get()
            response = session.serialize()
            session.key.delete()

        return jsonify(response)

    except Exception as e:
        return get_status_code(401)


messages = Blueprint('messages', __name__)


@messages.route('/users/<id>/messages', methods=['GET'])
def index(id):
    try:
        session = is_authenticated()

        if session and session.user.id() == long(id):
            args = request.args
            filter = args.get('filter', 'inbox')
            page = args.get('page', '1')
            offset = (int(page) - 1) * 20
            receipts = MessageReceipt.query(MessageReceipt.to_recipient == session.user and MessageReceipt.category == filter).fetch(20, offset=offset)
            messages = []

            if receipts:
                for i in receipts:
                    message = i.message.get()
                    message_json = {
                        "id": i.message.id(),
                        "subject": message.subject,
                        "body": message.body,
                        "timestamp": message.datetime_created
                    }
                    user = message.from_recipient.get()
                    user_json = {
                        "id": user.key.id(),
                        "email": user.email,
                        "last_name": user.last_name,
                        "first_name": user.first_name,
                        "middle_name": user.middle_name
                    }
                    data = {
                        "is_read": i.is_read,
                        "message": message_json,
                        "sender": user_json
                    }
                    messages.append(data)

            return jsonify(messages) # raises Exception?
        else:
            return get_status_code(401)
        
    except:
        return get_status_code(400)


@messages.route('/users/<user_id>/messages/<message_id>', methods=['GET'])
def show(user_id, message_id):
    session = is_authenticated()
    if session and session.user.id() == id:
        message = Message.query(long(id) == Message.id())
        mes_receipt = MessageReceipt.query(message.key == MessageReceipt.message)

    return jsonify({'error': {'status': 404, 'message': 'messages not found'}}), 404


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
    session = is_authenticated()

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
                    MessageReceipt(
                        message=message.key,
                        category='inbox',
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

    return get_status_code(400)