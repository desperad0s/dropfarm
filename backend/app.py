import logging
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from extensions import db, migrate, init_extensions
from models import create_tables, create_default_user
from routes import init_routes
from celery_tasks import run_goats_bot, update_statistics, start_bot_task, stop_bot_task

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
    
    CORS(app)
    api = Api(app)
    jwt = JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize extensions
    init_extensions(app)

    # Initialize routes
    init_routes(app)

    return app, socketio

app, socketio = create_app()

# Create tables and default user within the application context
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create all tables
    create_default_user()

if __name__ == '__main__':
    socketio.run(app, debug=True)