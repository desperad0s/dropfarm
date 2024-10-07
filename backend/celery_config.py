from celery import Celery

BROKER_URL = 'redis://localhost:6379/0'
RESULT_BACKEND = 'redis://localhost:6379/0'

celery_app = Celery('dropfarm',
                    broker=BROKER_URL,
                    backend=RESULT_BACKEND,
                    include=['tasks'])  # Changed from 'backend.tasks' to 'tasks'

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)