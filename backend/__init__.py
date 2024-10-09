from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate
from .celery_worker import celery

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Initialize Celery
    celery.conf.update(app.config)

    # Register blueprints
    from .routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api')

    return app
