from flask import Flask
from models import User
from pybcrypt import bcrypt

app = Flask(__name__)

@app.route('/')
def index():
	user = User()
	user.last_name = 'heh'
	user.first_name = 'heh'
	user.email = 'heh'
	hashed = bcrypt.hashpw('heh', bcrypt.gensalt())
	user.password = hashed
	user.put()
	return 'Hello World!'

if __name__ == '__main__':
	app.run()