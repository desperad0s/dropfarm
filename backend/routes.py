import logging
from flask import Blueprint, jsonify, request, make_response
from flask_cors import cross_origin
from .supabase_client import get_authenticated_client
from .tasks import start_recording_task, start_playback_task, stop_playback_task, delete_routine
from supabase import create_client, Client
from .config import Config

logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

def get_tokens():
    auth_header = request.headers.get('Authorization')
    refresh_token = request.headers.get('Refresh-Token')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, None
    return auth_header.split(' ')[1], refresh_token

@bot_routes.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

@bot_routes.route('/dashboard', methods=['GET'])
@cross_origin(supports_credentials=True)
def dashboard():
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401
        
        client = get_authenticated_client(access_token, refresh_token)
        
        user = client.auth.get_user()
        if not user.user:
            return jsonify({"error": "Failed to authenticate user"}), 401

        user_id = user.user.id

        # Fetch user stats
        user_stats = client.table('user_stats').select('*').eq('user_id', user_id).single().execute()
        
        # Fetch routines
        routines = client.table('routines').select('*').eq('user_id', user_id).execute()
        
        # Fetch recent activities
        activities = client.table('activities').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()

        dashboard_data = {
            'totalTokensGenerated': user_stats.data.get('total_tokens_generated', 0) if user_stats.data else 0,
            'totalRoutineRuns': user_stats.data.get('total_routine_runs', 0) if user_stats.data else 0,
            'lastRunDate': user_stats.data.get('last_run_date') if user_stats.data else None,
            'routines': routines.data,
            'activities': activities.data,
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bot_routes.route('/record', methods=['POST'])
@cross_origin(supports_credentials=True)
def record():
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401

        data = request.json
        routine_name = data.get('name')
        tokens_per_run = data.get('tokens_per_run')
        
        if not routine_name or tokens_per_run is None:
            return jsonify({"error": "Routine name and tokens per run are required"}), 400
        
        user = supabase.auth.get_user(access_token)
        if not user or not user.id:
            return jsonify({"error": "Failed to authenticate user"}), 401
        
        # Start recording task
        task = start_recording_task.delay(routine_name, tokens_per_run, user.id)
        return jsonify({
            "message": f"Recording task started for routine: {routine_name}",
            "task_id": task.id
        }), 202
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bot_routes.route('/start_playback', methods=['POST'])
@cross_origin(supports_credentials=True)
def start_playback():
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401

        data = request.json
        routine_name = data.get('name')
        repeat_indefinitely = data.get('repeat_indefinitely', False)
        
        if not routine_name:
            return jsonify({"error": "Routine name is required"}), 400
        
        user = supabase.auth.get_user(access_token)
        if not user or not user.id:
            return jsonify({"error": "Failed to authenticate user"}), 401
        
        # Start playback task
        task = start_playback_task.delay(routine_name, repeat_indefinitely, user.id)
        return jsonify({
            "message": f"Playback task started for routine: {routine_name}",
            "task_id": task.id
        }), 202
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bot_routes.route('/routines/<routine_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_routine_route(routine_id):
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401
        
        result = delete_routine.delay(routine_id, access_token, refresh_token)
        return jsonify({"msg": "Routine deletion task started"}), 202
    except Exception as e:
        logger.error(f"Error deleting routine: {str(e)}")
        return jsonify({"msg": str(e)}), 500

@bot_routes.route('/routines', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_routine():
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        if 'name' not in data:
            return jsonify({"error": "Routine name is required"}), 400
        if 'tokens_per_run' not in data:
            return jsonify({"error": "Tokens per run is required"}), 400

        client = get_authenticated_client(access_token, refresh_token)
        user = client.auth.get_user(access_token)
        if not user or not user.user:
            return jsonify({"error": "Failed to authenticate user"}), 401

        # Check if a routine with the same name already exists for this user
        existing_routine = client.table('routines').select('*').eq('name', data['name']).eq('user_id', user.user.id).execute()
        if existing_routine.data:
            return jsonify({"error": "A routine with this name already exists"}), 400

        routine = {
            'name': data['name'],
            'tokens_per_run': data['tokens_per_run'],
            'user_id': user.user.id,
            'steps': '[]'  # Initialize with empty steps
        }
        result = client.table('routines').insert(routine).execute()
        return jsonify(result.data[0]), 201
    except Exception as e:
        logger.error(f"Error adding routine: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bot_routes.route('/routines/<routine_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_routine(routine_id):
    try:
        access_token, refresh_token = get_tokens()
        if not access_token:
            return jsonify({"error": "No authentication token found"}), 401

        data = request.json
        client = get_authenticated_client(access_token, refresh_token)
        user = client.auth.get_user()
        if not user or not user.user:
            return jsonify({"error": "Failed to authenticate user"}), 401

        routine_update = {
            'name': data['name'],
            'tokens_per_run': data['tokens_per_run'],
        }
        result = client.table('routines').update(routine_update).eq('id', routine_id).eq('user_id', user.user.id).execute()
        if result.data:
            return jsonify(result.data[0]), 200
        else:
            return jsonify({"error": "Routine not found or you don't have permission to edit it"}), 404
    except Exception as e:
        logger.error(f"Error updating routine: {str(e)}")
        return jsonify({"error": str(e)}), 500
