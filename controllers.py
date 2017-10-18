from datetime import datetime
from flask import Blueprint, jsonify, request
from models import Message, MessageReceipt, Session, User
from pybcrypt import bcrypt

def is_authenticated():
    access_token = request.args.get('access_token')
    if access_token:
        session = Session.query(Session.access_token == access_token ).get()
        if session:
            return session
    return False

users = Blueprint('users', __name__)

@users.route('/users')
def index():
	return 'user'
    
@users.route('/users', methods=['POST'])
def create():
    user = User()
    user.last_name = request.form['last_name']
    user.first_name = request.form['first_name']
    user.email = request.form['email']
    user.password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
    user.put()

    return jsonify({
        'id': user.key.id(),
        'last_name': user.last_name,
        'first_name': user.first_name,
        'email': user.email
    })

@users.route('/users/<id>', methods=['GET'])
def show(id):
    user = User.get_by_id(int(id))
    return jsonify({
        'last_name': user.last_name,
        'first_name': user.first_name,
        'email': user.email
    })

@users.route('/users/<id>', methods=['PUT'])
def update(id):
    session = is_authenticated()
    if session:
        if session.user.id() == int(id):
            user = session.user.get()
            if request.form['last_name']:
                user.last_name = request.form['last_name']
            if request.form['first_name']:
                user.first_name = request.form['first_name']
            if request.form['password']:
                user.password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
            user.put()
            response = {
                'id': user.key.id(),
                'last_name': user.last_name,
                'first_name': user.first_name,
                'email': user.email
            }
            return jsonify(response)

    return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

@users.route('/users/<id>', methods=['DELETE'])
def destroy(id):
    session = is_authenticated()
    if session:
        if session.user.id() == int(id):
            user = session.user.get()
            response = {
                'id': user.key.id(),
                'last_name': user.last_name,
                'first_name': user.first_name,
                'email': user.email
            }
            user.key.delete()
            return jsonify(response)

    return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

sessions = Blueprint('sessions', __name__)

@sessions.route('/sessions', methods=['POST'])
def create():
    email = request.form['email']
    password = request.form['password']
    user = User.query(User.email == email).get()

    if user and bcrypt.hashpw(password, user.password) == user.password:
        session = Session(access_token=str(uuid4()), user=user.key)
        session.put()
        response = {
            'id': user.key.id(),
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'access_token': session.access_token
        }
        return jsonify(response)

    return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

@sessions.route('/sessions', methods=['DELETE'])
def destroy():
    session = is_authenticated()

    if session:
        user = session.user.get()
        response = {
            'id': user.key.id(),
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'access_token': session.access_token
        }
        session.key.delete()
        return jsonify(response)

    return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

messages = Blueprint('messages',__name__)

@messages.route('/users/<id>/messages', methods=['GET'])
def index(id):
    session = is_authenticated()
    if session and session.user.id() == id:
        filter = request.args.get('filter', 'inbox')
        page = request.args.get('page')
        received = MessageReceipt.query(session.user == MessageReceipt.to_recipient and filter == MessageReceipt.category).fetch()
        # if received:
        #     messages = Message.query(received.message_id).fetch(20,(page - 1)*20)
        #     return jsonify([k.to_dict() for k in messages])


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
    if session and session.user.id() == id:
        data = request.get_json()
        message = Message(
            subject=data['subject'],
            body=data['body'],
            user=session.user
        ).put()
        for recipient in data['recipients']:
            MessageReceipt(
                message=message,
                to_recipient=recipient
            ).put()