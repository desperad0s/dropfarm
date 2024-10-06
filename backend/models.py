import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
logger = logging.getLogger(__name__)

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    return conn

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  email TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  total_tasks_completed INTEGER DEFAULT 0,
                  total_rewards_earned REAL DEFAULT 0.0,
                  current_streak INTEGER DEFAULT 0)''')

    # Bot Settings table
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER UNIQUE,
                  is_active BOOLEAN DEFAULT FALSE,
                  run_interval INTEGER DEFAULT 60,
                  max_daily_runs INTEGER DEFAULT 5,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Bot Activities table
    c.execute('''CREATE TABLE IF NOT EXISTS bot_activities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  bot_type TEXT NOT NULL,
                  action TEXT NOT NULL,
                  result TEXT NOT NULL,
                  details TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT NOT NULL,
                  enabled BOOLEAN DEFAULT TRUE,
                  interval INTEGER DEFAULT 60,
                  max_daily_runs INTEGER DEFAULT 5,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()
    logger.info("Database tables created or already exist")

def create_default_user():
    from flask import current_app
    with current_app.app_context():
        default_username = "desperad0s"
        default_password = "hohoho"
        default_email = "desperad0s@example.com"

        user = User.get_by_username(default_username)
        if not user:
            hashed_password = generate_password_hash(default_password)
            User.create(default_username, hashed_password, default_email)
            logger.info(f"Default user '{default_username}' created")
        else:
            logger.info(f"Default user '{default_username}' already exists")

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_rewards_earned = db.Column(db.Float, default=0.0)
    current_streak = db.Column(db.Integer, default=0)

    @classmethod
    def get_by_username(cls, username):
        logger.debug(f"Attempting to get user with username: {username}")
        user = cls.query.filter_by(username=username).first()
        if user:
            logger.info(f"User found: {user.username}")
            logger.debug(f"User details: {user.to_dict()}")
        else:
            logger.warning(f"User not found: {username}")
        return user

    @classmethod
    def create(cls, username, password_hash, email):
        new_user = cls(username=username, password_hash=password_hash, email=email)
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

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
    bot_type = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def log(cls, user_id, bot_type, action, result, details=None):
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

# Call these functions to set up the database
create_tables()