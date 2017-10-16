from flask import Flask
from models import User
from pybcrypt import bcrypt
from controllers import users

app = Flask(__name__)
app.register_blueprint(users, url_prefix='/api/v1')

if __name__ == '__main__':
	app.run()
