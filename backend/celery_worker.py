from celery import Celery
from .config import Config

def make_celery(app_name=__name__):
    return Celery(
        app_name,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )

celery = make_celery()
celery.conf.update(Config.CELERY_CONFIG)

@celery.task
def cleanup_old_tasks():
    # Implement task cleanup logic here
    pass
