from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Update CORS configuration
    CORS(app, resources={r"/*": {"origins": Config.FRONTEND_URL}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])
    
    from .routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api')
    
    return app

# Import celery and tasks after create_app to avoid circular imports
from .celery_worker import celery
from . import tasks

__all__ = ('celery',)
