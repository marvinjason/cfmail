from flask import Flask
from models import User
from pybcrypt import bcrypt
from controllers import users,sessions

app = Flask(__name__)
app.register_blueprint(users, url_prefix='/api/v1')
app.register_blueprint(sessions, url_prefix='/api/v1')
app.debug = True

if __name__ == '__main__':
	app.run()
