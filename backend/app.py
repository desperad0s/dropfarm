from flask import Flask
from flask_cors import CORS
from .routes import bot_routes
from .auth import auth_bp
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}}, supports_credentials=True)

    app.register_blueprint(bot_routes, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app