from flask import Blueprint, request, jsonify
from models import User, Session
from pybcrypt import bcrypt
from uuid import uuid4

def is_authenticated():
    access_token = request.args.get('access_token')
    if access_token is not None:
        count = Session.query().filter(access_token=access_token).count()
        if count > 0:
            return True
    return False

users = Blueprint('users', __name__)
@users.route('/users/create', methods=['POST'])
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

@users.route('/users/update', methods=['PUT'])
def update():
    if is_authenticated():
        pass
    else:
        return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

@users.route('/users/destroy', methods=['DELETE'])
def destroy():
    if is_authenticated():
        access_token = request.args.get('access_token')
        session = Session.query().filter(access_token=access_token).fetch()[0]
        user = session.user.get()
        response = {
            'id': user.key.id(),
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'access_token': session.get().access_token
        }
        user.key.delete()
        return jsonify(response)
    else:
        return jsonify({'error': {'status': 401, 'message': 'unauthorized'}}), 401

@users.route('/users/<id>')
def show(id):
    user = User.query().filter(User.key == User.make_key(id)).count()
    return str(user)
    # return jsonify({
    #     'last_name': user.last_name,
    #     'first_name': user.first_name,
    #     'email': user.email
    # })

sessions = Blueprint('sessions', __name__)
@sessions.route('/sessions', methods=['POST'])
def create():
    pass