# Imports:
from ..constants import get_status_code
from flask import Blueprint, jsonify, request
from google.appengine.ext import ndb
from ..models.session_model import Session
from ..models.user_model import User


sessions = Blueprint('sessions', __name__)


@sessions.route('/sessions', methods=['POST'])
def create():
    try:
        data = request.get_json()
        email = (data['email'] if data['email']
                 else data['username'] if data['username']
                 else '')
        password = data.get('password', '')
        user = User.query(ndb.OR(User.email == email, User.username == email)).get()
        
        if not user or not user.equal_password(password):
            return get_status_code(401)

        session = Session(
            user_key=user.key,
            access_token=str(Session.make_access_token())
        )

        session.put()
        return jsonify(session.serialize(exclude=['id', 'datetime_updated']))

    except Exception as e:
        #return str(e)
        return get_status_code(400)


@sessions.route('/sessions', methods=['DELETE'])
def destroy():
    try:
        session = Session.query(Session.access_token == request.args.get('access_token', '')).get()

        if not session:
            return get_status_code(404)

        session.key.delete()

        return jsonify(session.serialize())

    except Exception as e:
        #return str(e)
        return get_status_code(400)