import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from .models import User, Routine, UserStats
from .extensions import db
from supabase import create_client, Client
from .config import Config
from .tasks import example_task
from datetime import datetime, timedelta
from functools import wraps
from .auth import verify_token

# Set up logger
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is malformed!'}), 401
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            current_user = verify_token(token)
            return f(current_user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401
    return decorated

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

@bot_routes.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    try:
        db_user = User.query.filter_by(supabase_uid=current_user['id']).first()
        if not db_user:
            db_user = User(email=current_user['email'], supabase_uid=current_user['id'])
            db.session.add(db_user)
            db.session.commit()
        
        stats = UserStats.query.filter_by(user_id=db_user.id).first()
        routines = Routine.query.filter_by(user_id=db_user.id).all()
        
        today = datetime.now()
        earnings_history = [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "amount": round(float(i) * 1.5, 2)}
            for i in range(30, 0, -1)
        ]
        
        activities = [
            {
                "timestamp": (today - timedelta(hours=i)).isoformat(),
                "action": f"Routine {i % 3 + 1} executed",
                "result": "Success" if i % 2 == 0 else "Failed"
            }
            for i in range(10)
        ]
        
        dashboard_data = {
            "email": db_user.email,
            "totalRoutineRuns": stats.routine_runs if stats else 0,
            "totalEarnings": stats.total_earnings if stats else 0.0,
            "lastRunDate": stats.last_run.isoformat() if stats and stats.last_run else None,
            "routines": [{"id": r.id, "name": r.name, "steps": r.steps} for r in routines],
            "earningsHistory": earnings_history,
            "activities": activities
        }
        
        return jsonify(dashboard_data), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
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

@bot_routes.route('/bot/toggle', methods=['POST'])
@token_required
def toggle_bot(current_user):
    try:
        db_user = User.query.filter_by(supabase_uid=current_user['id']).first()
        if not db_user:
            return jsonify({"msg": "User not found"}), 404
        
        status = request.json.get('status')
        if status is None:
            return jsonify({"msg": "Missing status in request body"}), 400
        
        # Here you would implement the logic to actually start or stop the bot
        action = "started" if status else "stopped"
        return jsonify({"msg": f"Bot {action} successfully"}), 200
    except Exception as e:
        logger.error(f"Error toggling bot status: {str(e)}")
        return jsonify({"msg": str(e)}), 500

@bot_routes.route('/routines', methods=['POST'])
@token_required
def add_routine(current_user):
    try:
        db_user = User.query.filter_by(supabase_uid=current_user['id']).first()
        if not db_user:
            return jsonify({"msg": "User not found"}), 404
        
        routine_data = request.json
        new_routine = Routine(
            name=routine_data['name'],
            steps=routine_data['steps'],
            user_id=db_user.id
        )
        db.session.add(new_routine)
        db.session.commit()
        
        return jsonify({"msg": "Routine added successfully", "id": new_routine.id}), 201
    except Exception as e:
        logger.error(f"Error adding routine: {str(e)}")
        return jsonify({"msg": str(e)}), 500

@bot_routes.route('/routines/<int:routine_id>', methods=['PUT'])
@token_required
def edit_routine(current_user, routine_id):
    try:
        db_user = User.query.filter_by(supabase_uid=current_user['id']).first()
        if not db_user:
            return jsonify({"msg": "User not found"}), 404
        
        routine = Routine.query.filter_by(id=routine_id, user_id=db_user.id).first()
        if not routine:
            return jsonify({"msg": "Routine not found"}), 404
        
        routine_data = request.json
        routine.name = routine_data['name']
        routine.steps = routine_data['steps']
        routine.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({"msg": "Routine updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error editing routine: {str(e)}")
        return jsonify({"msg": str(e)}), 500