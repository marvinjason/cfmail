from flask import Blueprint

users = Blueprint('users', __name__)
@users.route('/users')
def index():
    return 'users'

@users.route('/users/<id>')
def show(id):
    return 'user ' + id