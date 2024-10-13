from .celery_worker import celery
from .recorder import start_recording
from .player import start_playback
from .supabase_client import supabase
import json
import logging
from celery.exceptions import SoftTimeLimitExceeded
from .utils import sanitize_data
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
        logger.info(f"Starting recording task for routine: {routine_name}")
        result = start_recording(routine_name)
        logger.info(f"Recording result: {result}")
        if result and result.get('actions'):
            sanitized_result = sanitize_data(result)
            try:
                # Check if the routine already exists
                existing_routine = supabase.table('routines').select('*').eq('name', routine_name).eq('user_id', user_id).execute()
                
                if existing_routine.data:
                    # Update existing routine
                    update_result = supabase.table('routines').update({
                        'steps': json.dumps(sanitized_result),
                        'tokens_per_run': tokens_per_run,
                        'updated_at': 'now()'
                    }).eq('name', routine_name).eq('user_id', user_id).execute()
                    logger.info(f"Routine updated in database: {update_result}")
                else:
                    # Insert new routine
                    insert_result = supabase.table('routines').insert({
                        'name': routine_name,
                        'user_id': user_id,
                        'steps': json.dumps(sanitized_result),
                        'tokens_per_run': tokens_per_run
                    }).execute()
                    logger.info(f"New routine saved to database: {insert_result}")
                
                return f"Recording completed for routine: {routine_name}"
            except Exception as e:
                logger.error(f"Failed to save routine: {str(e)}")
                raise
        else:
            logger.warning(f"No actions recorded for routine: {routine_name}")
            return f"No actions recorded for routine: {routine_name}"
    except SoftTimeLimitExceeded:
        logger.error(f"Recording task timed out for routine: {routine_name}")
        return f"Recording task timed out for routine: {routine_name}"
    except Exception as e:
        logger.error(f"Error during recording: {str(e)}")
        raise

def delete_routine(routine_name):
    try:
        supabase.table('routines').delete().eq('name', routine_name).execute()
        logging.info(f"Deleted routine: {routine_name}")
    except Exception as e:
        logging.error(f"Failed to delete routine: {str(e)}")

@celery.task(bind=True)
def run_routine(self, routine_id, user_id):
    routine = supabase.table('routines').select('*').eq('id', routine_id).single().execute()
    if not routine.data:
        return "Routine not found"
    
    steps = json.loads(routine.data['steps'])
    # Implement the logic to run the routine steps
    # ...

    # Update user stats
    supabase.table('user_stats').upsert({
        'user_id': user_id,
        'total_routine_runs': supabase.raw('total_routine_runs + 1')
    }).execute()

    return f"Routine {routine.data['name']} completed"

@celery.task(bind=True, name='backend.tasks.start_playback_task', max_retries=0, soft_time_limit=None, time_limit=None)
def start_playback_task(self, routine_name, user_id, repeat_indefinitely=False):
    logging.info(f"Starting playback for routine: {routine_name}")
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)
        
        # Log the start of playback
        try:
            supabase.table('activities').insert({
                'user_id': user_uuid,
                'action_type': 'playback_start',
                'details': json.dumps({'routine_name': routine_name, 'repeat_indefinitely': repeat_indefinitely})
            }).execute()
        except Exception as e:
            logging.error(f"Failed to log playback start: {str(e)}")
        
        routines = supabase.table('routines').select('*').eq('name', routine_name).eq('user_id', user_id).execute()
        logging.info(f"Retrieved routines: {routines.data}")
        
        if not routines.data:
            return f"Routine not found: {routine_name}"
        
        if len(routines.data) > 1:
            logging.warning(f"Multiple routines found with name '{routine_name}'. Using the most recent one.")
            routine = max(routines.data, key=lambda x: x['created_at'])
        else:
            routine = routines.data[0]
        
        recorded_data = routine['steps']
        logging.info(f"Recorded data: {recorded_data}")
        
        if isinstance(recorded_data, str):
            recorded_data = json.loads(recorded_data)
        
        if isinstance(recorded_data, list):
            actions = recorded_data
        elif isinstance(recorded_data, dict) and 'actions' in recorded_data:
            actions = recorded_data['actions']
        else:
            raise ValueError(f"Unexpected recorded_data format: {type(recorded_data)}")
        
        logging.info(f"Loaded {len(actions)} actions for playback")
        
        if not actions:
            logging.warning("No actions to play")
            return "No actions to play"
        
        player = start_playback(routine_name, {'actions': actions}, repeat_indefinitely)
        
        # Store task ID in a way that can be accessed for cleanup
        celery.backend.set(f'playback_task:{user_id}:{routine_name}', self.request.id)
        
        player.play()
        
        # Clean up task ID after completion
        celery.backend.delete(f'playback_task:{user_id}:{routine_name}')
        
        # Log the completion of playback
        try:
            supabase.table('activities').insert({
                'user_id': str(user_uuid),  # Convert UUID to string
                'action_type': 'playback_complete',
                'details': json.dumps({'routine_name': routine_name})
            }).execute()
        except Exception as e:
            logging.error(f"Failed to log playback completion: {str(e)}")
        
        logging.info(f"Playback completed for routine: {routine_name}")
        return f"Playback completed for routine: {routine_name}"
    except Exception as e:
        # Clean up task ID in case of error
        celery.backend.delete(f'playback_task:{user_id}:{routine_name}')
        # Log the error
        try:
            supabase.table('activities').insert({
                'user_id': user_uuid,
                'action_type': 'playback_error',
                'details': json.dumps({'routine_name': routine_name, 'error': str(e)})
            }).execute()
        except Exception as log_error:
            logging.error(f"Failed to log playback error: {str(log_error)}")
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
    try:
        calibration = supabase.table('user_calibrations').select('*').eq('user_id', user_id).order('updated_at', desc=True).limit(1).execute()
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

def get_dashboard_data(user_id):
    try:
        # Fetch user stats
        user_stats = supabase.table('user_stats').select('*').eq('user_id', user_id).single().execute()
        
        # Fetch routines
        routines = supabase.table('routines').select('*').eq('user_id', user_id).execute()
        
        # Fetch recent activities
        activities = supabase.table('activities').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        
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
