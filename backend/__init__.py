from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    # Register blueprints
    from .routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api')

    return app
