from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import logging

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and register blueprints
from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Import models
from models import User, BotConfig, AirdropProject

if __name__ == '__main__':
    app.run(debug=True)