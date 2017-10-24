# Imports:
from ..constants import get_status_code
from datetime import datetime
from flask import Blueprint, jsonify, request
from ..models.session_model import Session
from ..models.user_model import User


users = Blueprint('users', __name__)


@users.route('/users')
def index():
    try:
	    return 'user'

    except Exception as e:
        #return str(e)
        return get_status_code(401)


@users.route('/users', methods=['POST'])
def create():
    try:
        data = request.get_json()

        if User.exist_username(data['username']):
            return get_status_code(409)

        user = User()

        for k, v in data.iteritems():
            v = (User.encrypt_password(v) if k == 'password'
                else datetime.strptime(v, '%Y-%m-%d').date() if k == 'birthdate'
                else v)

            exec("user.{0} = v".format(k))

        user.put()
        return jsonify(user.serialize(exclude=['password']))

    except Exception as e:
        #return str(e)
        return get_status_code(400)


@users.route('/users/<user_id>', methods=['GET'])
def show(user_id):
    try:
        user_id = long(user_id)
        user = User.get_by_id(user_id)
        
        if not user:
            return get_status_code(401)

        return jsonify(
            user.serialize() if Session.authenticate(user_id, request.args.get('access_token', ''))
            else user.serialize(include=['username', 'email'])
        )

    except Exception as e:
        #return str(e)
        return get_status_code(400)


@users.route('/users/<user_id>', methods=['PUT'])
def update(user_id):
    try:
        session = Session.authenticate(user_id, request.args.get('access_token', ''))
        
        if not session:
            return get_status_code(401)
        
        data = request.get_json()
        user = session.user_key.get()
        updates = ['username', 'email']
        
        for k, v in data.iteritems():
            if k in ['username', 'email', 'birthdate' 'age',
                    'datetime_created', 'datetime_udpated']:
                continue

            v = User.encrypt_password(v) if k == 'password' else v
            exec("user.{0} = v".format(k))
            updates.append(k)

        user.put()
        return jsonify(user.serialize(include=updates))

    except Exception as e:
        #return str(e)
        return get_status_code(400)


@users.route('/users/<user_id>', methods=['DELETE'])
def destroy(user_id):
    return get_status_code(405)

    try:
        session = Session.authenticate(user_id, request.args['access_token'])

        if not session:
            return get_status_code(401)

        user = session.user_key.get()
        user.key.delete()
            
        return jsonify(user.serialize())

    except Exception as e:
        return get_status_code(400)