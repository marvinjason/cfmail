from constants import get_status_code
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
    form = request.form

    if User.exists(form['username']):
        return get_status_code(400)
    
    user = User()
    user.username = form.get('username', '')
    user.password = bcrypt.hashpw(form['password'], bcrypt.gensalt())
    user.first_name = form.get('first_name', '')
    user.middle_name = form.get('middle_name', '')
    user.last_name = form.get('last_name', '')
    user.sex = form.get('sex', '')
    user.birthdate = datetime.strptime(form['birthdate'], '%M/%d/%Y')
    user.contact_number = form.get('contact_number', '')
    user.address = form.get('address', '')
    user.postal_code = form.get('postal_code', '')
    user.country = form.get('country', '')
    user.put()

    return jsonify(user.serialize())

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