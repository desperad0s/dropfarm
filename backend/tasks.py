from .celery_worker import celery

@celery.task
def example_task():
    return "Task completed"
