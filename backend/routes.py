from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import logging

# Set up logger
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

@bot_routes.route('/login', methods=['POST', 'OPTIONS'])
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

def init_app(app):
    app.register_blueprint(bot_routes, url_prefix='/api')