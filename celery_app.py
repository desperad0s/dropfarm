from celery import Celery
from supabase import create_client, Client
import os

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

class SupabaseBackend(object):
    def __init__(self):
        self.client = supabase

    def store_result(self, task_id, result, status):
        self.client.table('celery_results').insert({
            'task_id': task_id,
            'result': result,
            'status': status
        }).execute()

    def get_result(self, task_id):
        response = self.client.table('celery_results').select('*').eq('task_id', task_id).execute()
        if response.data:
            return response.data[0]['result']
        return None

celery_app.conf.result_backend = SupabaseBackend()

# Add this to ensure Celery tasks can be imported
celery_app.autodiscover_tasks(['backend.tasks'])