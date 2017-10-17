from flask import Blueprint, request, jsonify
from models import User, Session
from pybcrypt import bcrypt
from uuid import uuid4

def is_authenticated():
    access_token = request.args.get('access_token')
    if access_token:
        session = Session.query(Session.access_token == access_token).get()
        if session:
            return session
    return False

users = Blueprint('users', __name__)

@users.route('/users', methods=['POST'])
def create():
    user = User()
    user.last_name = request.form['last_name']
    user.first_name = request.form['first_name']
    user.email = request.form['email']
    user.password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
    user.put()
    session = Session(access_token=str(uuid4()), user=user.key).put()
    return jsonify({
        'id': user.key.id(),
        'last_name': user.last_name,
        'first_name': user.first_name,
        'email': user.email,
        'access_token': session.get().access_token
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
