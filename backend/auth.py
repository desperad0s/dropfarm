from flask import Blueprint, request, jsonify
from supabase import create_client, Client
from .config import Config
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({"token": response.session.access_token}), 200
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({"error": str(e)}), 400

def verify_token(token):
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        return {
            'id': user.id,
            'email': user.email,
            'aud': user.aud,
            # Remove the 'role' field
        }
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise ValueError('Invalid token')

# Add other auth routes here