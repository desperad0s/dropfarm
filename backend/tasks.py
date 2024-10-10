from .celery_worker import celery
from .recorder import start_recording, start_playback
from .supabase_client import supabase
import json
import logging
from celery.exceptions import SoftTimeLimitExceeded

@celery.task(bind=True, name='backend.tasks.start_recording_task', max_retries=0, soft_time_limit=600, time_limit=610)
def start_recording_task(self, routine_name, tokens_per_run, user_id):
    logging.info(f"Starting recording for routine: {routine_name}")
    try:
        result = start_recording(routine_name)
        if result and len(result) > 0:
            try:
                supabase.table('routines').insert({
                    'name': routine_name,
                    'user_id': user_id,
                    'steps': json.dumps(result),
                    'tokens_per_run': tokens_per_run
                }).execute()
                logging.info(f"Recording completed and saved for routine: {routine_name}")
                return f"Recording completed for routine: {routine_name}"
            except Exception as e:
                logging.error(f"Failed to save routine: {str(e)}")
                delete_routine(routine_name)
                raise
        else:
            logging.error(f"No actions recorded for routine: {routine_name}")
            delete_routine(routine_name)
            return f"No actions recorded for routine: {routine_name}"
    except SoftTimeLimitExceeded:
        logging.error(f"Recording time limit exceeded for routine: {routine_name}")
        delete_routine(routine_name)
        return f"Recording time limit exceeded for routine: {routine_name}"
    except Exception as e:
        logging.error(f"Error during recording: {str(e)}")
        delete_routine(routine_name)
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
        routine = supabase.table('routines').select('*').eq('name', routine_name).eq('user_id', user_id).single().execute()
        if not routine.data:
            return f"Routine not found: {routine_name}"
        
        actions = json.loads(routine.data['steps'])
        result = start_playback(routine_name, actions)
        
        if result:
            logging.info(f"Playback completed for routine: {routine_name}")
            return f"Playback completed for routine: {routine_name}"
        else:
            logging.error(f"Playback failed for routine: {routine_name}")
            return f"Playback failed for routine: {routine_name}"
    except Exception as e:
        logging.error(f"Error during playback: {str(e)}")
        raise