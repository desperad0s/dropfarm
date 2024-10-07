from celery import Celery
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_celery_app():
    app = Celery('dropfarm',
                 broker='amqp://guest:guest@localhost:5672//',
                 backend='rpc://',
                 include=['backend.tasks'])  # Change this back to 'backend.tasks'

    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_pool='solo',  # Use this for Windows
    )

    return app

celery_app = create_celery_app()