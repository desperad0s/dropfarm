from .celery_worker import celery
from .recorder import start_recording
from .player import start_playback
from .supabase_client import supabase
import json
import logging
from celery.exceptions import SoftTimeLimitExceeded
from .utils import sanitize_data

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

@celery.task(bind=True, name='backend.tasks.start_playback_task', max_retries=0, soft_time_limit=600, time_limit=610)
def start_playback_task(self, routine_name, user_id):
    logging.info(f"Starting playback for routine: {routine_name}")
    try:
        routines = supabase.table('routines').select('*').eq('name', routine_name).eq('user_id', user_id).execute()
        if not routines.data:
            return f"Routine not found: {routine_name}"
        
        if len(routines.data) > 1:
            logging.warning(f"Multiple routines found with name '{routine_name}'. Using the most recent one.")
            routine = max(routines.data, key=lambda x: x['created_at'])
        else:
            routine = routines.data[0]
        
        recorded_data = json.loads(routine['steps'])
        logging.info(f"Loaded {len(recorded_data['actions'])} actions for playback")
        
        result = start_playback(routine_name, recorded_data)
        
        if result:
            logging.info(f"Playback completed for routine: {routine_name}")
            return f"Playback completed for routine: {routine_name}"
        else:
            logging.error(f"Playback failed for routine: {routine_name}")
            return f"Playback failed for routine: {routine_name}"
    except Exception as e:
        logging.error(f"Error during playback: {str(e)}")
        raise

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
