from app import create_app
from extensions import celery, init_celery

app = create_app()
init_celery(app)