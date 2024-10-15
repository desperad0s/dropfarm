import httpx
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from .config import Config

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

class SupabaseClient:
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }

    def table(self, table_name):
        return TableQuery(self, table_name)

class TableQuery:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.base_url = f"{client.url}/rest/v1/{table_name}"

    def select(self, *columns):
        url = self.base_url
        if columns:
            url += f"?select={','.join(columns)}"
        response = httpx.get(url, headers=self.client.headers)
        response.raise_for_status()
        return response.json()

    def insert(self, data):
        response = httpx.post(self.base_url, json=data, headers=self.client.headers)
        response.raise_for_status()
        return response.json()

    def update(self, data):
        response = httpx.patch(self.base_url, json=data, headers=self.client.headers)
        response.raise_for_status()
        return response.json()

    def delete(self):
        response = httpx.delete(self.base_url, headers=self.client.headers)
        response.raise_for_status()
        return response.json()

def get_supabase_client():
    return SupabaseClient()

def get_authenticated_client(access_token, refresh_token=None):
    # For now, we'll just return the global supabase client
    # In the future, you might want to use the tokens to create a new client or authenticate the existing one
    return supabase

def authenticated_request(access_token, refresh_token=None):
    user = supabase.auth.get_user(access_token)
    return user.user if user else None
