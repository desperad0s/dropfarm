from celery import Celery
from app import create_app

flask_app = create_app()
celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
celery.conf.update(flask_app.config)

@celery.task
def example_task():
    # Define your tasks here
    pass