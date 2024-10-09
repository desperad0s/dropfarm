from flask import Flask
from celery import Celery
from backend.config import Config

def create_celery_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    celery = Celery(app.name)
    celery.config_from_object(app.config["CELERY"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = create_celery_app()