import httpx
from .config import Config  # Changed this line

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

def get_authenticated_client(access_token: str, refresh_token: str = None):
    client = get_supabase_client()
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client

def authenticated_request(access_token: str, refresh_token: str):
    client = get_authenticated_client(access_token, refresh_token)
    response = httpx.get(f"{client.url}/auth/v1/user", headers=client.headers)
    response.raise_for_status()
    return response.json()
