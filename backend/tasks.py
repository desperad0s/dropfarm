from celery import shared_task
from .celery_worker import celery
from .recorder import start_recording_task
from .supabase_client import supabase
import json

@celery.task
def run_routine(routine_id, user_id):
    routine = supabase.table('routines').select('*').eq('id', routine_id).single().execute()
    if not routine.data:
        return "Routine not found"
    
    steps = json.loads(routine.data['steps'])
    # Implement the logic to run the routine steps
    # ...

    # Update user stats
    supabase.table('user_stats').upsert({
        'user_id': user_id,
        'routine_runs': supabase.raw('routine_runs + 1')
    }).execute()

    return f"Routine {routine.data['name']} completed"

@celery.task
def start_recording(routine_name, user_id):
    result = start_recording_task(routine_name)
    # Save the recorded routine
    supabase.table('routines').insert({
        'name': routine_name,
        'user_id': user_id,
        'steps': json.dumps(result)
    }).execute()
    return f"Recording completed for routine: {routine_name}"

@shared_task
def example_task():
    return "This is an example task"

@shared_task
def start_recording(routine_name):
    return start_recording_task(routine_name)
