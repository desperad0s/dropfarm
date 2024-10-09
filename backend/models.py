from .extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime  # Add this import

# Define your models here
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supabase_uid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Remove the role field if it's not in your database

    def __init__(self, email, supabase_uid):
        self.email = email
        self.supabase_uid = supabase_uid

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    steps = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    routine_runs = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    last_run = db.Column(db.DateTime)