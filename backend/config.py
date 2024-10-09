import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:dropfarmpostgres@localhost:5432/dropfarm')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Celery configuration
    CELERY = {
        'broker_url': os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'timezone': 'UTC',
        'enable_utc': True,
        'worker_pool': 'solo',  # For Windows compatibility
    }

    FRONTEND_URL = 'http://localhost:3000'  # Adjust if your frontend runs on a different port

    @staticmethod
    def init_app(app):
        pass