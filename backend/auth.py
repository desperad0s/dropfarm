from flask import request, jsonify
from functools import wraps
from .supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

def verify_token(token):
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            logging.info(f"Verified token for user ID: {user.user.id}")
            return user.user
        logging.warning("Token verification failed: User not found")
        return None
    except Exception as e:
        logging.error(f"Token verification failed: {str(e)}")
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            current_user = verify_token(token)
            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Remove the auth_bp and other unnecessary functions
