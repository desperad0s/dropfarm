from flask import Flask
from flask_cors import CORS
from .config import Config
from .celery_worker import celery as celery_app
from .supabase_client import supabase

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}}, supports_credentials=True)
    
    from .routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api')
    
    return app

# Import tasks after creating the app to avoid circular imports
from . import tasks

__all__ = ('celery_app',)
