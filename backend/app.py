from flask import Flask, make_response
from flask_cors import CORS
from .config import Config
from .routes import bot_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "Refresh-Token"],
        "supports_credentials": True
    }})
    
    @app.after_request
    def after_request(response):
        # Remove any existing Access-Control-Allow-Origin header
        response.headers.pop('Access-Control-Allow-Origin', None)
        # Set the header only once
        response.headers.set('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, Access-Control-Allow-Credentials, Refresh-Token')
        return response
    
    app.register_blueprint(bot_routes, url_prefix='/api')
    
    return app
