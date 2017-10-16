from flask import Flask
from models import User
from pybcrypt import bcrypt

app = Flask(__name__)

if __name__ == '__main__':
	app.run()
