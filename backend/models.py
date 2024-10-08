from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CeleryTaskResult(db.Model):
    __tablename__ = 'celery_task_results'
    id = db.Column(db.String(36), primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String)

class TemporaryData(db.Model):
    __tablename__ = 'temporary_data'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String)
    expiry = db.Column(db.DateTime)