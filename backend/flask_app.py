from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate
from routes import bot_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(bot_routes, url_prefix='/api')

    return app