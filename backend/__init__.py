from flask import Flask
from flask_cors import CORS
from .config import Config
from .celery_worker import celery as celery_app
from .supabase_client import supabase

__all__ = ('celery_app',)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}}, supports_credentials=True)
    
    from .routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api')
    
    return app

# Import tasks to ensure they are registered
from . import tasks

# Explicitly import and register the playback task
from .tasks import start_playback_task
celery_app.task(start_playback_task)
