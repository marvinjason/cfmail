from flask import Flask
from static.models import User
from static.controllers import users, sessions, messages

app = Flask(__name__)
app.register_blueprint(users, url_prefix='/api/v1')
app.register_blueprint(sessions, url_prefix='/api/v1')
app.register_blueprint(messages, url_prefix='/api/v1')
app.debug = True

@app.route('/')
def index():
	return 'cfmail app'
	
if __name__ == '__main__':
	app.run()