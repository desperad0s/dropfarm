import logging
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from extensions import db, migrate, init_extensions
from models import create_tables, create_default_user
from backend.celery_app import create_celery_app
from datetime import timedelta
import redis

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Extend to 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Set refresh token to 30 days
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    api = Api(app)
    jwt = JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize extensions
    init_extensions(app)

    # Initialize Celery
    celery = create_celery_app(app)

    # Import and register routes
    from routes import init_routes
    init_routes(app)

    # Create tables and default user within the application context
    with app.app_context():
        db.create_all()  # Create all tables
        create_default_user()

    return app, socketio, celery

app, socketio, celery = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)