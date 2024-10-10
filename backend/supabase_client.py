from supabase import create_client, Client
from .config import Config

supabase: Client = None

def init_supabase():
    global supabase
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

init_supabase()