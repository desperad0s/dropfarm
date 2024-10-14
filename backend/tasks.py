from .celery_worker import celery
from .recorder import start_recording
from .player import start_playback
from .supabase_client import supabase
import json
import logging
from celery.exceptions import SoftTimeLimitExceeded
from .utils import sanitize_data, uuid_json_dumps
from celery.result import AsyncResult
from celery.app.control import Inspect, Control
from uuid import UUID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def update_recording_status(user_id, routine_name, status):
    key = f"recording_status:{user_id}:{routine_name}"
    celery.backend.set(key, status)

def get_recording_status(user_id, routine_name):
    key = f"recording_status:{user_id}:{routine_name}"
    return celery.backend.get(key)

@celery.task(bind=True, name='backend.tasks.start_recording_task', max_retries=0, soft_time_limit=600, time_limit=610)
def start_recording_task(self, routine_name, tokens_per_run, user_id):
    try:
        result = start_recording(routine_name)
        if result and result.get('actions'):
            sanitized_result = sanitize_data(result)
            supabase.table('routines').insert({
                'name': routine_name,
                'user_id': user_id,
                'steps': json.dumps(sanitized_result),
                'tokens_per_run': tokens_per_run
            }).execute()
            
            supabase.table('activities').insert({
                'user_id': user_id,
                'action_type': 'recording_completed',
                'details': json.dumps({'routine_name': routine_name})
            }).execute()
            
            return f"Recording completed for routine: {routine_name}"
        else:
            return f"No actions recorded for routine: {routine_name}"
    except Exception as e:
        logging.error(f"Error during recording: {str(e)}")
        raise

@celery.task
def delete_routine(routine_id, access_token, refresh_token=None):
    try:
        client = get_authenticated_client(access_token, refresh_token)
        user = client.auth.get_user()
        if not user or not user.user:
            raise ValueError("Failed to authenticate user")
        
        result = client.table('routines').delete().eq('id', routine_id).execute()
        if result.data:
            logging.info(f"Deleted routine: {routine_id}")
            return f"Routine {routine_id} deleted successfully"
        else:
            logging.warning(f"Routine not found or not deleted: {routine_id}")
            return f"Routine {routine_id} not found or could not be deleted"
    except Exception as e:
        logging.error(f"Failed to delete routine: {str(e)}")
        raise

@celery.task
def run_routine(routine_id, user_id, access_token):
    try:
        client = get_authenticated_client(access_token)
        routine = client.table('routines').select('*').eq('id', routine_id).single().execute()
        if not routine.data:
            return "Routine not found"
        
        steps = json.loads(routine.data['steps'])
        # Implement the logic to run the routine steps
        # This might involve calling the player or other functions
        # For now, we'll just log that the routine was "run"
        logging.info(f"Running routine: {routine.data['name']}")

        # Update user stats
        client.table('user_stats').upsert({
            'user_id': user_id,
            'total_routine_runs': client.table('user_stats').raw('total_routine_runs + 1')
        }).execute()

        return f"Routine {routine.data['name']} completed"
    except Exception as e:
        logging.error(f"Error running routine: {str(e)}")
        raise

@celery.task(bind=True, name='backend.tasks.start_playback_task', max_retries=0, soft_time_limit=None, time_limit=None)
def start_playback_task(self, routine_name, repeat_indefinitely, user_id):
    try:
        routine = supabase.table('routines').select('*').eq('name', routine_name).eq('user_id', user_id).single().execute()
        if not routine.data:
            raise ValueError(f"Routine not found: {routine_name}")

        steps = json.loads(routine.data['steps'])
        player = start_playback(routine_name, steps, repeat_indefinitely)
        
        tokens_generated = routine.data['tokens_per_run']
        runs_completed = player.get_iteration_count() if repeat_indefinitely else 1

        supabase.table('user_stats').upsert({
            'user_id': user_id,
            'total_routine_runs': supabase.raw(f'total_routine_runs + {runs_completed}'),
            'total_tokens_generated': supabase.raw(f'total_tokens_generated + {tokens_generated * runs_completed}'),
            'last_run_date': 'now()'
        }).execute()

        supabase.table('activities').insert({
            'user_id': user_id,
            'action_type': 'playback_completed',
            'details': json.dumps({
                'routine_name': routine_name,
                'tokens_generated': tokens_generated * runs_completed,
                'runs_completed': runs_completed
            })
        }).execute()

        return f"Playback completed for routine: {routine_name}"
    except Exception as e:
        logging.error(f"Error during playback: {str(e)}")
        raise

@celery.task(name='backend.tasks.stop_playback_task')
def stop_playback_task(task_id):
    try:
        task = AsyncResult(task_id)
        if task.state == 'PLAYING':
            player = task.info.get('player')
            if player:
                player.stop()
                return "Playback stopped successfully"
        return "No active playback found to stop"
    except Exception as e:
        logging.error(f"Error stopping playback: {str(e)}")
        return f"Error stopping playback: {str(e)}"

def revoke_task(task_id):
    control = Control(celery)
    control.revoke(task_id, terminate=True)

@celery.task(name='backend.tasks.cleanup_playback_task')
def cleanup_playback_task(user_id, routine_name):
    task_id = celery.backend.get(f'playback_task:{user_id}:{routine_name}')
    if task_id:
        revoke_task(task_id)
        celery.backend.delete(f'playback_task:{user_id}:{routine_name}')

def get_user_calibration_data(user_id):
    client = get_authenticated_client(None)  # You might need to handle this differently
    try:
        calibration = client.table('user_calibrations').select('*').eq('user_id', user_id).order('updated_at', desc=True).limit(1).execute()
        if calibration.data:
            calibration_data = calibration.data[0]
            return {
                'browser': json.loads(calibration_data.get('browser_calibration') or '[]'),
                'recorder': json.loads(calibration_data.get('recorder_calibration') or '[]'),
                'player': json.loads(calibration_data.get('player_calibration') or '[]'),
                'aspect_ratio': calibration_data.get('aspect_ratio')
            }
        else:
            logger.warning(f"No calibration data found for user {user_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving calibration data: {str(e)}")
        return None

def get_dashboard_data(user_id, access_token):
    client = get_authenticated_client(access_token)
    try:
        # Fetch user stats
        user_stats = client.table('user_stats').select('*').eq('user_id', user_id).single().execute()
        
        # Fetch routines
        routines = client.table('routines').select('*').eq('user_id', user_id).execute()
        
        # Fetch recent activities
        activities = client.table('activities').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        
        # Calculate total earnings and tokens generated
        total_earnings = user_stats.data.get('total_earnings', 0) if user_stats.data else 0
        total_tokens_generated = user_stats.data.get('total_tokens_generated', 0) if user_stats.data else 0
        
        return {
            'totalEarnings': total_earnings,
            'totalTokensGenerated': total_tokens_generated,
            'totalRoutineRuns': user_stats.data.get('total_routine_runs', 0) if user_stats.data else 0,
            'lastRunDate': user_stats.data.get('last_run_date') if user_stats.data else None,
            'routines': routines.data,
            'activities': activities.data if activities else [],
            'earningsHistory': []  # You might want to implement this if needed
        }
    except Exception as e:
        logging.error(f"Error fetching dashboard data: {str(e)}")
        raise

@celery.task
def some_task(access_token, refresh_token=None):
    client = get_authenticated_client(access_token, refresh_token)
    # Use client for Supabase operations

@celery.task
def start_recording_task(routine_name, user_id):
    # Implement recording logic
    # Update activities table
    supabase.table('activities').insert({
        'user_id': user_id,
        'action_type': 'recording_started',
        'details': json.dumps({'routine_name': routine_name})
    }).execute()

@celery.task
def start_playback_task(routine_name, user_id, repeat_indefinitely):
    # Implement playback logic
    # Update activities and user_stats tables
    supabase.table('activities').insert({
        'user_id': user_id,
        'action_type': 'playback_started',
        'details': json.dumps({'routine_name': routine_name, 'repeat_indefinitely': repeat_indefinitely})
    }).execute()
    
    # Update user_stats after playback completes
    supabase.table('user_stats').update({
        'total_routine_runs': supabase.raw('total_routine_runs + 1'),
        'last_run_date': 'now()'
    }).eq('user_id', user_id).execute()