from celery import Celery

BROKER_URL = 'redis://localhost:6379/0'
RESULT_BACKEND = 'redis://localhost:6379/0'

celery_app = Celery('dropfarm',
                    broker=BROKER_URL,
                    backend=RESULT_BACKEND,
                    include=['backend.tasks'])  # Change this back to 'backend.tasks'

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='solo',  # Add this line for Windows compatibility
)