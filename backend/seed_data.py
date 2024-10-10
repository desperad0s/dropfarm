from .supabase_client import supabase
import uuid
from datetime import datetime

def seed_data(user_id=None):
    if user_id is None:
        user_id = str(uuid.uuid4())
    
    # Check if user_stats already exists
    existing_stats = supabase.table('user_stats').select('*').eq('user_id', user_id).execute()
    if not existing_stats.data:
        # Seed user_stats
        user_stats = {
            'user_id': user_id,
            'total_routine_runs': 10,  # Changed from 'routine_runs' to 'total_routine_runs'
            'total_earnings': 100.50,
            'last_run_date': datetime.utcnow().isoformat()
        }
        supabase.table('user_stats').insert(user_stats).execute()

    # Check if routines already exist
    existing_routines = supabase.table('routines').select('*').eq('user_id', user_id).execute()
    if not existing_routines.data:
        # Seed routines
        routines = [
            {'name': 'Test Routine 1', 'steps': ['Step 1', 'Step 2'], 'tokens_per_run': 5, 'user_id': user_id},
            {'name': 'Test Routine 2', 'steps': ['Step A', 'Step B', 'Step C'], 'tokens_per_run': 10, 'user_id': user_id}
        ]
        for routine in routines:
            supabase.table('routines').insert(routine).execute()

    print("Seed data inserted successfully")

if __name__ == "__main__":
    seed_data()