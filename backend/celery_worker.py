from celery import Celery
from .config import Config
from celery.contrib.abortable import AbortableTask

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )
    celery.conf.update(Config.CELERY_CONFIG)
    
    # Add task base
    celery.Task = AbortableTask
    
    return celery

celery = make_celery()

@celery.task
def cleanup_old_tasks():
    # Implement task cleanup logic here
    pass

# Import tasks here to ensure they are registered
from . import tasks
