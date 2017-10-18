from constants import get_status_code
from datetime import datetime
from flask import Blueprint, jsonify, request
from google.appengine.ext import ndb
from models import Message, MessageReceipt, Session, User
from pybcrypt import bcrypt
from uuid import getnode as get_mac


def is_authenticated():
    access_token = request.args.get('access_token')
    token_count = 0
    
    if access_token:
        token_count = (Session.query(ndb.AND(Session.access_token == access_token,
                                             Session.mac_address == get_mac())).count())
        
    return token_count > 0


users = Blueprint('users', __name__)


@users.route('/users')
def index():
	return 'user'
    

@users.route('/users', methods=['POST'])
def create():
    try:
        data = request.get_json()

        if User.exists(data['username']):
            return get_status_code(400)
        
        user = User()
        
        for k, v in data.iteritems():
            v = (bcrypt.hashpw(v, bcrypt.gensalt()) if k == 'password'
                else datetime.strptime(v, '%M/%d/%Y').date() if k == 'birthdate'
                else v)

            exec("user.{0} = v".format(k))

        user.put()
    except:
        return get_status_code(400)

    return jsonify(user.serialize())


@users.route('/users/<id>', methods=['GET'])
def show(id):
    user = User.get_by_id(int(id))
    return jsonify(user.serialize())


@users.route('/users/<id>', methods=['PUT'])
def update(id):
    session = is_authenticated()

    if session:
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

    return get_status_code(401)


@users.route('/users/<id>', methods=['DELETE'])
def destroy(id):
    session = is_authenticated()

    if session:
        if session.user.id() == int(id):
            user = session.user.get()
            response = user.serialize()
            user.key.delete()
            
            return jsonify(response)

    return get_status_code(401)


sessions = Blueprint('sessions', __name__)


@sessions.route('/sessions', methods=['POST'])
def create():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query(User.email == email).get()

    if user and bcrypt.hashpw(password, user.password) == user.password:
        session = Session(access_token=str(uuid4()), user=user.key)
        session.put()

        return jsonify(response.serialize())

    return get_status_code(401)


@sessions.route('/sessions', methods=['DELETE'])
def destroy():
    session = is_authenticated()

    if session:
        user = session.user.get()
        response = session.serialize()
        session.key.delete()

        return jsonify(response)

    return get_status_code(401)


messages = Blueprint('messages',__name__)


@messages.route('/users/<id>/messages', methods=['GET'])
def index(id):
    session = is_authenticated()
    if session and session.user.id() == id:
        filter = request.args.get('filter', 'inbox')
        page = request.args.get('page')
        received = MessageReceipt.query(session.user == MessageReceipt.to_recipient and filter == MessageReceipt.category).fetch(20,(page-1)*20)
        if received:
            messages = Message.query(received.message_id).fetch(20,(page - 1)*20)
            return jsonify([k.to_dict() for k in messages])
    return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

@messages.route('/users/<user_id>/messages/<message_id>', methods=['GET'])
def show(user_id, message_id):
    session = is_authenticated()
    if session and session.user.id() == user_id:

        return jsonify({'error': {'status': 404, 'message': 'messages not found'}}), 404

@messages.route('/users/<id>/messages', methods=['POST'])
def create(id):
    # JSON:
    #     {
    #         "subject": "My Subject",
    #         "body": "My Body",
    #         "recipients": [
    #             'email1@cfmail.com',
    #             'email2@cfmail.com',
    #             'email3@cfmail.com'
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
                        to_recipient=user.key
                    ).put()
                )

        response = {
            'id': message.key.id(),
            'subject': message.subject,
            'body': message.body,
            'recipients': [{'id': i.id(), 'email': i.get().email} for i in message_recipients],
            'timestamp': message.datetime_created
        }

        return jsonify(response)

    return get_status_code(400)
