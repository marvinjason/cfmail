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
        'email': user.email,

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
                user.password = request.form['password']
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

sessions = Blueprint('sessions',__name__)
@sessions.route('/sessions',methods=['POST'])
def createj():
    email = request.form['email']
    password = request.form['password']

    user = User.query(User.email == email  ).get()
    if bcrypt.hashpw(password, user.password) == user.password:
        session = Session(user=user.key)
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