from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class BotActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_rewards_earned = db.Column(db.Float, default=0.0)
    current_streak = db.Column(db.Integer, default=0)