import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:dropfarmpostgres@localhost:5432/dropfarm')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Celery configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    # Add other configuration variables as needed

    FRONTEND_URL = 'http://localhost:3000'  # Adjust if your frontend runs on a different port

    @staticmethod
    def init_app(app):
        pass