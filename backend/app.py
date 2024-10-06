from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db, create_tables, create_default_user
from routes import init_routes
from flask_socketio import SocketIO
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
CORS(app)
api = Api(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the database
db.init_app(app)
with app.app_context():
    create_tables()
    db.create_all()
    create_default_user()  # Call create_default_user() here

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)