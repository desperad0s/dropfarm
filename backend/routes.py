import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from .models import User, Routine, UserStats
from .extensions import db
from supabase import create_client, Client
from .config import Config
from .tasks import example_task

# Set up logger
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

@bot_routes.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, supabase_uid=response.user.id)
            db.session.add(user)
            db.session.commit()
        return jsonify(access_token=response.session.access_token), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401

@bot_routes.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        user = User(email=email, supabase_uid=response.user.id)
        db.session.add(user)
        db.session.commit()
        return jsonify(access_token=response.session.access_token), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@bot_routes.route('/dashboard', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def dashboard():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    
    try:
        user = supabase.auth.get_user(token.split()[1])
        db_user = User.query.filter_by(supabase_uid=user.id).first()
        if not db_user:
            return jsonify({"msg": "User not found"}), 404
        
        stats = UserStats.query.filter_by(user_id=db_user.id).first()
        routines = Routine.query.filter_by(user_id=db_user.id).all()
        
        dashboard_data = {
            "email": db_user.email,
            "routineRuns": stats.routine_runs if stats else 0,
            "totalEarnings": stats.total_earnings if stats else 0.0,
            "lastRun": stats.last_run.isoformat() if stats and stats.last_run else None,
            "routines": [{"id": r.id, "name": r.name} for r in routines]
        }
        
        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401

@bot_routes.route('/run-task', methods=['POST'])
@cross_origin(supports_credentials=True)
def run_task():
    task = example_task.delay()
    return jsonify({"task_id": task.id}), 202

@bot_routes.route('/test-celery', methods=['GET'])
def test_celery():
    task = example_task.delay()
    return jsonify({"message": "Task started", "task_id": task.id}), 202
