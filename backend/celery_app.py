from celery import Celery

def create_celery_app(app=None):
    celery = Celery(
        'dropfarm',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['backend.tasks']
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_pool='solo',  # Use this for Windows
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = create_celery_app()