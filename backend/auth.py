from flask import Blueprint, request, jsonify
from supabase import create_client
from .config import Config

auth_bp = Blueprint('auth', __name__)

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({"token": response.session.access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Add other auth routes here