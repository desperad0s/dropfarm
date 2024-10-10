import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from functools import wraps
from datetime import datetime, timedelta
from .models import User, Routine, UserStats
from .supabase_client import supabase
from .config import Config
from .tasks import example_task, start_recording
from .auth import verify_token

# Set up logger
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

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
            if current_user is None:
                return jsonify({'message': 'Token is invalid!'}), 401
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
            # Replace db.session with Supabase queries
            # For example:
            # supabase.table('users').insert({"email": email, "supabase_uid": response.user.id}).execute()
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
        # Replace db.session with Supabase queries
        # For example:
        # supabase.table('users').insert({"email": email, "supabase_uid": response.user.id}).execute()
        return jsonify(access_token=response.session.access_token), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@bot_routes.route('/dashboard', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_dashboard(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        # Log the current user's ID
        logging.info(f"Fetching dashboard data for user ID: {current_user.id}")
        
        # Fetch user stats
        user_stats = supabase.table('user_stats').select('*').eq('user_id', str(current_user.id)).execute()
        logging.info(f"User stats query result: {user_stats}")
        
        # If user_stats doesn't exist, create default data
        if not user_stats.data:
            logging.info("User stats not found, creating default data")
            default_stats = {
                'user_id': str(current_user.id),
                'total_routine_runs': 0,
                'total_earnings': 0,
                'last_run_date': None
            }
            insert_result = supabase.table('user_stats').insert(default_stats).execute()
            logging.info(f"Insert result: {insert_result}")
            user_stats = supabase.table('user_stats').select('*').eq('user_id', str(current_user.id)).execute()

        # Fetch routines
        routines = supabase.table('routines').select('*').eq('user_id', str(current_user.id)).execute()
        logging.info(f"Routines query result: {routines}")
        
        dashboard_data = {
            'totalEarnings': user_stats.data[0]['total_earnings'] if user_stats.data else 0,
            'earningsHistory': [],  # Implement this based on your data structure
            'activities': [],  # Implement this based on your data structure
            'totalRoutineRuns': user_stats.data[0]['total_routine_runs'] if user_stats.data else 0,
            'lastRunDate': user_stats.data[0].get('last_run_date'),
            'routines': [{'id': str(r['id']), 'name': r['name'], 'tokens_per_run': r['tokens_per_run']} for r in routines.data] if routines.data else [],
            'totalTokensGenerated': sum(r['tokens_per_run'] for r in routines.data) if routines.data else 0
        }
        
        return jsonify(dashboard_data), 200
    except Exception as e:
        logging.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'message': 'Error fetching dashboard data'}), 500

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
        routine_data = request.json
        new_routine = {
            'name': routine_data['name'],
            'steps': routine_data['steps'],
            'tokens_per_run': routine_data['tokens_per_run'],
            'user_id': str(current_user.id)
        }
        result = supabase.table('routines').insert(new_routine).execute()
        
        return jsonify({"msg": "Routine added successfully", "id": result.data[0]['id']}), 201
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
        
        # Replace db.session with Supabase queries
        # For example:
        # supabase.table('routines').update({"name": routine_data['name'], "steps": routine_data['steps'], "updated_at": datetime.utcnow()}).eq('id', routine_id).execute()
        
        return jsonify({"msg": "Routine updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error editing routine: {str(e)}")
        return jsonify({"msg": str(e)}), 500

@bot_routes.route('/record', methods=['POST'])
@token_required
def record_routine(current_user):
    routine_name = request.json.get('name')
    if not routine_name:
        return jsonify({"error": "Routine name is required"}), 400
    
    try:
        task = start_recording.delay(routine_name)
        return jsonify({"message": f"Recording task started for routine: {routine_name}", "task_id": task.id}), 202
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bot_routes.route('/save_routine', methods=['POST'])
@token_required
def save_recorded_routine(current_user):
    routine_name = request.json.get('name')
    result = save_routine(routine_name)
    return jsonify({"message": result}), 200

@bot_routes.route('/load_routine', methods=['POST'])
@token_required
def load_saved_routine(current_user):
    routine_name = request.json.get('name')
    result = load_routine(routine_name)
    return jsonify({"message": result}), 200

@bot_routes.route('/playback', methods=['POST'])
@token_required
def playback_saved_routine(current_user):
    url = 'https://web.telegram.org/k/'  # Fixed URL for now
    routine_name = request.json.get('name')
    if not routine_name:
        return jsonify({"error": "Routine name is required"}), 400
    
    result = playback_routine(url)
    return jsonify({"message": result}), 200

@bot_routes.route('/translate_headless', methods=['POST'])
@token_required
def translate_routine_to_headless(current_user):
    routine_name = request.json.get('name')
    result = translate_to_headless(routine_name)
    return jsonify({"message": result}), 200

@bot_routes.route('/populate_test_data', methods=['POST'])
@token_required
def populate_test_data(current_user):
    try:
        # Create user stats if not exists
        user_stats = supabase.table('user_stats').select('*').eq('user_id', str(current_user.id)).single().execute()
        if not user_stats.data:
            supabase.table('user_stats').insert({
                'user_id': str(current_user.id),
                'routine_runs': 10,
                'total_earnings': 100.50,
                'last_run': datetime.utcnow().isoformat()
            }).execute()

        # Add some sample routines
        sample_routines = [
            {'name': 'Sample Routine 1', 'steps': ['Step 1', 'Step 2'], 'tokens_per_run': 5, 'user_id': str(current_user.id)},
            {'name': 'Sample Routine 2', 'steps': ['Step A', 'Step B', 'Step C'], 'tokens_per_run': 10, 'user_id': str(current_user.id)}
        ]
        for routine in sample_routines:
            supabase.table('routines').insert(routine).execute()

        return jsonify({"message": "Test data populated successfully"}), 200
    except Exception as e:
        logging.error(f"Error populating test data: {str(e)}")
        return jsonify({'message': 'Error populating test data'}), 500