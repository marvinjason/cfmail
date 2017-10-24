# Imports:
from ..constants import MESSAGE_CATEGORIES as CATEGORIES
from ..constants import MESSENGER_ROLES as ROLES
from ..constants import get_status_code
from flask import Blueprint, jsonify, request
from google.appengine.ext import ndb
from ..models.message_model import Message
from ..models.message_pointer_model import MessagePointer
from ..models.session_model import Session
from ..models.user_model import User


messages = Blueprint('messages', __name__)


@messages.route('/users/<user_id>/messages', methods=['GET'])
def index(user_id):
    try:
        args = request.args
        session = Session.authenticate(user_id, args.get('access_token', ''))

        if not session:
            return get_status_code(401)

        filter = args.get('filter', CATEGORIES[0])
        role = (ROLES[0] if filter in CATEGORIES[:2] else
                ROLES[1] if filter in CATEGORIES[2:]
                else '')
        page = args.get('page', '1')
        count = int(args.get('count', 20))
        offset = (int(page) - 1) * count
        messages = []
        
        if not filter in CATEGORIES or not role in ROLES:
            return get_status_code(404)

        pointers = MessagePointer.query(ndb.AND(MessagePointer.recipient == session.user_key,
                                                MessagePointer.role == role,
                                                MessagePointer.category == filter)).fetch(count, offset=offset)
        
        for p in pointers:
            message = p.message_key.get().serialize(include=['to_recipients', 'subject', 'body'])
            message.update(p.serialize(exclude=['datetime_created', 'datetime_updated', 'recipient']))
            messages.append(message)
            
        return jsonify(messages)

    except Exception as e:
        return str(e)
        return get_status_code(400)


@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['GET'])
def show(user_id, pointer_id):

    try:
        args = request.args
        session = Session.authenticate(user_id, args.get('access_token', ''))

        if not session:
            return get_status_code(401)

        pointer = MessagePointer.get_by_id(pointer_id)

        if not pointer:
            return get_status_code(404)

        message = pointer.message_key.get().serialize(include=['subject', 'body'])
        message.update(pointer.serialize(exclude=['datetime_created', 'datetime_updated', 'to_recipients']))
        
        return message

    except Exception as e:
        return get_status_code(400)


@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['DELETE'])
def destroy(user_id, pointer_id):
    try:
        args = request.args
        session = Session.authenticate(user_id, args.get('access_token', ''))

        if not session:
            return get_status_code(401)

        pointer = MessagePointer.get_by_id(pointer_id)

        if not pointer:
            return get_status_code(404)

        if MessagePointer.query(MessagePointer.message_key == pointer.message_key).count() <= 1:
            pointer.message_key.delete()

        pointer.key.delete()
        return jsonify(pointer.serialize())
        
    except Exception as e:
        return get_status_code(404)


@messages.route('/users/<user_id>/messages', methods=['POST'])
def create(user_id):
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
        args = request.args
        session = Session.authenticate(user_id, args.get('access_token', ''))

        if not session:
            return get_status_code(401)

        data = request.get_json()
        category = data.get('category', CATEGORIES[2])
        recipients = ([User.query(User.email == r).get().key for r in data['recipients']]
                      if data['recipients'] else [])
        
        if not category in CATEGORIES[2:]:
            return get_status_code(403)
        
        message = Message(
            from_recipient=session.user_key,
            to_recipients=recipients,
            subject=data.get('subject', ''),
            body=data.get('body', '')
        )
        message.put()
        
        pointer = MessagePointer(
            message_key=message.key,
            role=ROLES[1],
            recipient=User.get_by_id(long(user_id)).key,
            category=category
        )
        pointer.put()

        if not message or not pointer:
            return get_status_code(400)
        
        if category == CATEGORIES[3]:
            if len(recipients) <= 0:
                return get_status_code(403)

            for r in recipients:
                user = User.query(User.key == r).get()

                if not user:
                    continue

                pointer = MessagePointer(
                    message_key=message.key,
                    role=ROLES[0],
                    recipient=user.key,
                    category=CATEGORIES[0]
                )
                pointer.put()

        return jsonify(message.serialize())

    except Exception as e:
        return str(e)
        return get_status_code(400)


@messages.route('/users/<user_id>/messages/<pointer_id>', methods=['PUT'])
def update(user_id, pointer_id):
    try:
        args = request.args
        session = Session.authenticate(user_id, args.get('access_token', 0))

        if not session:
            return get_status_code(401)

        data = request.get_json()
        pointer = MessagePointer.get_by_id(pointer_id)

        if not pointer:
            return get_status_code(404)

        role = pointer.role

        category = data.get('category', pointer.category)
        is_read = data.get('is_read', pointer.is_read)

        if role == ROLES[0]:
            pointer.category = data.get('category', pointer.category)
            pointer.is_read = data.get('is_read', pointer.is_read)
            pointer.put()

            return jsonify(pointer.serialize())

        elif role == ROLES[1]:
            message = pointer.message_key.get()

            if not message:
                return get_status_code(404)

            message.to_recipients = data.get('recipients', message.to_recipients)
            message.subject = data.get('subject', message.subject)
            message.body = data.get('body', message.body)
            message.put()

            if category == CATEGORIES[3]:
                if len(recipients) <= 0:
                    return get_status_code(403)

                for r in message.to_recipients:
                    user = User.query(User.email == r)

                    if not user:
                        continue

                    pointer = MessagePointer(
                        message_key=message.key,
                        role=ROLES[0],
                        recipient=user.key,
                        category=category
                    )
                    pointer.put()

            return jsonify(message.serialize())

        else:
            return get_status_code(403)


    except Exception as e:
        #return str(e)
        return get_status_code(400)