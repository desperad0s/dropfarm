from celery import Celery
from .config import Config

celery = Celery(__name__)
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND

# If you have any celery beat schedule, you can add it here
# celery.conf.beat_schedule = {
#     'example-task': {
#         'task': 'your_app.tasks.example_task',
#         'schedule': 300.0,
#     },
# }