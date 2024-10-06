import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from extensions import db, jwt, celery
from flask_cors import CORS

# Load environment variables
load_dotenv()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Initialize Celery
    celery.conf.update(app.config)

    # Initialize Flask-Migrate
    Migrate(app, db)

    # Import and register blueprints
    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()

# Import models
from models.models import User, BotConfig, AirdropProject, BotActivity

if __name__ == '__main__':
    app.run(debug=True)