# Imports:
from flask import Flask
from static.controllers.messages_controller import messages
from static.controllers.sessions_controller import sessions
from static.controllers.users_controller import users

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