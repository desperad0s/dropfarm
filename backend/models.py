import sqlite3
from datetime import datetime
from extensions import db
import logging
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    return conn

def create_tables():
    db.create_all()
    logger.info("Database tables created or already exist")

def create_default_user():
    default_username = "desperad0s"
    default_password = "password123"
    default_email = "desperad0s@example.com"

    logger.debug(f"Attempting to get user with username: {default_username}")
    user = User.get_by_username(default_username)

    if user is None:
        logger.info(f"Creating default user: {default_username}")
        User.create(default_username, default_password, default_email)
        logger.info("Default user created successfully")
    else:
        logger.info("Default user already exists")

class User(db.Model):
    __tablename__ = 'users'  # Add this line to specify the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_rewards_earned = db.Column(db.Float, default=0.0)
    current_streak = db.Column(db.Integer, default=0)
    bot_task_id = db.Column(db.String(36), nullable=True)

    @classmethod
    def create(cls, username, password, email):
        hashed_password = generate_password_hash(password)
        user = cls(username=username, password_hash=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        return user.id

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'total_tasks_completed': self.total_tasks_completed,
            'total_rewards_earned': self.total_rewards_earned,
            'current_streak': self.current_streak
        }

    @classmethod
    def update_statistics(cls, user_id, tasks_completed, rewards_earned, streak):
        user = cls.query.get(user_id)
        if user:
            user.total_tasks_completed += tasks_completed
            user.total_rewards_earned += rewards_earned
            user.current_streak = streak
            db.session.commit()

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    interval = db.Column(db.Integer, default=60)
    max_daily_runs = db.Column(db.Integer, default=5)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'enabled': self.enabled,
            'interval': self.interval,
            'max_daily_runs': self.max_daily_runs
        }

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    run_interval = db.Column(db.Integer, default=60)
    max_daily_runs = db.Column(db.Integer, default=5)

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def create_or_update(cls, user_id, is_active, run_interval, max_daily_runs):
        settings = cls.get_by_user_id(user_id)
        if settings:
            settings.is_active = is_active
            settings.run_interval = run_interval
            settings.max_daily_runs = max_daily_runs
        else:
            settings = cls(user_id=user_id, is_active=is_active, run_interval=run_interval, max_daily_runs=max_daily_runs)
            db.session.add(settings)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'is_active': self.is_active,
            'run_interval': self.run_interval,
            'max_daily_runs': self.max_daily_runs
        }

class BotActivity(db.Model):
    __tablename__ = 'bot_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bot_type = db.Column(db.String(50), nullable=True)  # Change this to nullable=True
    action = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def log(cls, user_id, action, result, bot_type=None, details=None):
        activity = cls(user_id=user_id, bot_type=bot_type, action=action, result=result, details=details)
        db.session.add(activity)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'bot_type': self.bot_type,
            'action': self.action,
            'result': self.result,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def get_recent_activities(cls, user_id, limit):
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).limit(limit).all()

class EarningsEntry(db.Model):
    __tablename__ = 'earnings_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime("%Y-%m-%d"),
            'amount': self.amount
        }

class BotStatistics(db.Model):
    __tablename__ = 'bot_statistics'  # Add this line to specify the table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tasks_completed = db.Column(db.Integer, default=0)
    rewards_earned = db.Column(db.Float, default=0)
    streak = db.Column(db.Integer, default=0)
    total_runtime = db.Column(db.Float, default=0)
    errors_encountered = db.Column(db.Integer, default=0)

    def update_stats(self, new_stats):
        self.tasks_completed = new_stats['tasks_completed']
        self.rewards_earned = new_stats['rewards_earned']
        self.streak = new_stats['streak']
        self.total_runtime = new_stats['total_runtime']
        self.errors_encountered = new_stats['errors_encountered']