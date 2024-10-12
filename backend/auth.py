from flask import Blueprint, request, jsonify
from .supabase_client import supabase
from .config import Config
from .models import User  # Add this import
from .seed_data import seed_data
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_id = response.user.id
        seed_data(user_id)  # Seed data for the user
        return jsonify({"token": response.session.access_token}), 200
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        user_id = response.user.id
        seed_data(user_id)  # Seed data for the new user
        return jsonify({"token": response.session.access_token}), 200
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({"error": str(e)}), 400

def verify_token(token):
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            logging.info(f"Verified token for user ID: {user.user.id}")
            return User(id=user.user.id, email=user.user.email)
        logging.warning("Token verification failed: User not found")
        return None
    except Exception as e:
        logging.error(f"Token verification failed: {str(e)}")
        return None

# Add other auth routes here
