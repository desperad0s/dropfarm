import logging
from flask import Blueprint, jsonify, request, render_template
from flask_cors import cross_origin
from functools import wraps
from datetime import datetime, timedelta
from .models import User, Routine, UserStats
from .supabase_client import supabase
from .config import Config
from .tasks import start_recording_task, start_playback_task, get_recording_status
from .auth import verify_token
from .celery_worker import celery
import signal
from celery.result import AsyncResult
import json
from .recorder import Recorder
from .player import Player

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
    return jsonify({"message": "Task functionality is being updated"}), 202

@bot_routes.route('/test-celery', methods=['GET'])
def test_celery():
    return jsonify({"message": "Celery test functionality is being updated"}), 202

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
    data = request.json
    logging.info(f"Received record request: {data}")
    routine_name = data.get('name')
    tokens_per_run = data.get('tokens_per_run')
    if not routine_name or tokens_per_run is None:
        logging.error(f"Missing required data: name={routine_name}, tokens_per_run={tokens_per_run}")
        return jsonify({"error": "Routine name and tokens per run are required"}), 400
    
    try:
        task = start_recording_task.apply_async(args=[routine_name, tokens_per_run, str(current_user.id)], expires=600)
        return jsonify({
            "message": f"Recording task started for routine: {routine_name}",
            "task_id": task.id,
            "routine_name": routine_name
        }), 202
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
    routine_name = request.json.get('name')
    if not routine_name:
        return jsonify({"error": "Routine name is required"}), 400
    
    try:
        task = start_playback_task.delay(routine_name, str(current_user.id))
        return jsonify({"message": f"Playback task started for routine: {routine_name}", "task_id": task.id}), 202
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@bot_routes.route('/cancel_recording', methods=['POST'])
@token_required
def cancel_recording(current_user):
    task_id = request.json.get('task_id')
    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400
    
    # Use SIGTERM instead of SIGKILL
    celery.control.revoke(task_id, terminate=True, signal='SIGTERM')
    
    # Delete the routine data if it exists
    routine_name = request.json.get('routine_name')
    if routine_name:
        try:
            supabase.table('routines').delete().eq('name', routine_name).eq('user_id', str(current_user.id)).execute()
            logging.info(f"Deleted routine: {routine_name}")
        except Exception as e:
            logging.error(f"Failed to delete routine: {str(e)}")
    
    return jsonify({"message": "Recording cancelled successfully"}), 200

@bot_routes.route('/recording-status/<task_id>', methods=['GET'])
@token_required
def get_recording_status(current_user, task_id):
    try:
        task = AsyncResult(task_id)
        status = task.state
        if status == 'PENDING':
            return jsonify({'status': 'in_progress'})
        elif status == 'SUCCESS':
            return jsonify({'status': 'completed'})
        elif status == 'FAILURE':
            return jsonify({'status': 'failed'})
        else:
            return jsonify({'status': 'unknown'})
    except Exception as e:
        logging.error(f"Error getting recording status: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bot_routes.route('/calibrate', methods=['POST'])
@token_required
def calibrate(current_user):
    calibration_data = request.json.get('calibration_data')
    calibration_type = request.json.get('type')
    aspect_ratio = request.json.get('aspect_ratio')
    if not calibration_data or not calibration_type:
        logging.error(f"Missing calibration data or type: data={calibration_data}, type={calibration_type}")
        return jsonify({"error": "Calibration data and type are required"}), 400
    
    try:
        user_id = str(current_user.id)
        logging.info(f"Calibrating for user {user_id}, type: {calibration_type}")
        
        # Fetch existing calibration data
        existing_calibration = supabase.table('user_calibrations').select('*').eq('user_id', user_id).execute()
        logging.info(f"Existing calibration data: {existing_calibration.data}")
        
        update_data = {
            'user_id': user_id,
            'updated_at': 'now()',
            f'{calibration_type}_calibration': json.dumps(calibration_data),
            'calibration_data': json.dumps({calibration_type: calibration_data})  # Add this line
        }
        
        # If there's existing data, merge it with the new data
        if existing_calibration.data:
            existing_data = existing_calibration.data[0]  # Get the first (and should be only) row
            existing_calibration_data = json.loads(existing_data.get('calibration_data', '{}'))
            existing_calibration_data[calibration_type] = calibration_data
            update_data['calibration_data'] = json.dumps(existing_calibration_data)
        
        if aspect_ratio is not None:
            update_data['aspect_ratio'] = aspect_ratio
        
        logging.info(f"Updating calibration data: {update_data}")
        result = supabase.table('user_calibrations').upsert(update_data).execute()
        logging.info(f"Calibration update result: {result}")
        
        return jsonify({"message": f"{calibration_type.capitalize()} calibration data saved successfully"}), 200
    except Exception as e:
        logging.error(f"Error saving calibration data: {str(e)}")
        return jsonify({"error": f"Failed to save calibration data: {str(e)}"}), 500

@bot_routes.route('/recorder_calibration')
@token_required
def recorder_calibration(current_user):
    return render_template('recorder_calibration.html')

@bot_routes.route('/player_calibration')
@token_required
def player_calibration(current_user):
    return render_template('player_calibration.html')

@bot_routes.route('/get_calibration_points', methods=['GET'])
@token_required
def get_calibration_points(current_user):
    calibration_points = [
        {"x": 0, "y": 0}, {"x": 0.5, "y": 0}, {"x": 1, "y": 0},
        {"x": 0, "y": 0.5}, {"x": 0.5, "y": 0.5}, {"x": 1, "y": 0.5},
        {"x": 0, "y": 1}, {"x": 0.5, "y": 1}, {"x": 1, "y": 1}
    ]
    return jsonify(calibration_points)

@bot_routes.route('/api/start_recorder_calibration', methods=['POST'])
@token_required
def start_recorder_calibration(current_user):
    try:
        logger.info(f"Starting recorder calibration for user {current_user.id}")
        recorder = Recorder("calibration")
        recorder.perform_recorder_calibration()
        logger.info(f"Recorder calibration completed for user {current_user.id}")
        return jsonify({"message": "Recorder calibration started"}), 200
    except Exception as e:
        logger.error(f"Error starting recorder calibration for user {current_user.id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bot_routes.route('/api/start_player_calibration', methods=['POST'])
@token_required
def start_player_calibration(current_user):
    try:
        logger.info(f"Starting player calibration for user {current_user.id}")
        player = Player("calibration")
        player.perform_player_calibration()
        logger.info(f"Player calibration completed for user {current_user.id}")
        return jsonify({"message": "Player calibration started"}), 200
    except Exception as e:
        logger.error(f"Error starting player calibration for user {current_user.id}: {str(e)}")
        return jsonify({"error": str(e)}), 500