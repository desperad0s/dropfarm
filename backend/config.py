import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Frontend URL
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:3000'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    CELERY_CONFIG = {
        'broker_url': CELERY_BROKER_URL,
        'result_backend': CELERY_RESULT_BACKEND,
        'accept_content': ['json'],
        'task_serializer': 'json',
        'result_serializer': 'json',
        'timezone': 'UTC',
        'task_always_eager': False,
        'worker_concurrency': 1,
        'worker_max_tasks_per_child': 1,
        'worker_pool': 'solo',
    }

    # Add other configuration variables as needed