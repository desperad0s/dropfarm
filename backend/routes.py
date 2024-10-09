from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_cors import cross_origin
from .tasks import get_bot_status, get_recorded_routines
import logging

# Set up logger
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

@bot_routes.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    logger.info(f"Login attempt for email: {email}")

    # Here, you should verify the user's credentials
    # For now, we'll just create a token if email and password are provided
    if email and password:
        access_token = create_access_token(identity=email)
        logger.info(f"Login successful for email: {email}")
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Login failed for email: {email}")
        return jsonify({"msg": "Bad email or password"}), 401

@bot_routes.route('/dashboard', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin(supports_credentials=True)
def dashboard():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    current_user = get_jwt_identity()
    logger.info(f"Dashboard request for user: {current_user}")
    
    # For now, return some dummy data
    dashboard_data = {
        "botStatus": "Stopped",
        "recentActivities": [],
        "projects": [],
        "earnings": {"total": 0, "lastMonth": 0, "history": []}
    }
    
    return jsonify(dashboard_data), 200

@bot_routes.route('/bot/recorded_routines', methods=['GET'])
@jwt_required()
@cross_origin(supports_credentials=True)
def recorded_routines():
    # ... (rest of your recorded_routines logic)

@bot_routes.route('/bot/status', methods=['GET'])
@jwt_required()
@cross_origin(supports_credentials=True)
def bot_status():
    # ... (rest of your bot_status logic)

def init_app(app):
    app.register_blueprint(bot_routes, url_prefix='/api')