from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, create_refresh_token, jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, BotSettings, BotActivity, Project, BotStatistics
from extensions import db
import random
from datetime import datetime, timedelta
import logging
from backend.celery_app import celery_app
from backend.tasks import initialize_bot, start_routine, stop_routine, stop_bot, get_bot_status, playback_routine
from backend.recorder import recorder
import os

# Set up logger
logger = logging.getLogger(__name__)

# Global variable to store earnings data (temporary solution)
EARNINGS_DATA = {
    "total": 0,
    "lastMonth": 0,
    "history": []
}

def generate_earnings_data():
    global EARNINGS_DATA
    today = datetime.now()
    EARNINGS_DATA["history"] = [
        {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), 
         "amount": round(random.uniform(0.1, 10.0), 2)} 
        for i in range(30)
    ]
    EARNINGS_DATA["total"] = round(sum(entry["amount"] for entry in EARNINGS_DATA["history"]), 2)
    EARNINGS_DATA["lastMonth"] = round(sum(entry["amount"] for entry in EARNINGS_DATA["history"][:30]), 2)

# Generate initial data
generate_earnings_data()

def log_activity(user_id, action, result, bot_type=None, details=None):
    new_activity = BotActivity(
        user_id=user_id,
        bot_type=bot_type,
        action=action,
        result=result,
        details=details
    )
    db.session.add(new_activity)
    db.session.commit()

RECORDED_ROUTINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_routines')

def get_recorded_routines():
    return [f.replace('_actions.json', '') for f in os.listdir(RECORDED_ROUTINES_DIR) if f.endswith('_actions.json')]

def init_routes(app):
    bot_routes = Blueprint('bot_routes', __name__)
    
    @bot_routes.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        logger.info(f"Registration attempt for username: {username}, email: {email}")

        if not username or not email or not password:
            logger.warning("Registration attempt with missing data")
            return jsonify({'message': 'Missing required fields'}), 400

        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration failed: Username {username} already exists")
            return jsonify({'message': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed: Email {email} already exists")
            return jsonify({'message': 'Email already exists'}), 400

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User registered successfully: {username}")
            return jsonify({'message': 'User registered successfully'}), 201
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return jsonify({'message': 'An error occurred during registration'}), 500

    @bot_routes.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        logger.info(f"Login attempt for username: {username}")

        if not username or not password:
            logger.warning("Login attempt with missing username or password")
            return jsonify({"msg": "Missing username or password"}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            logger.info(f"Login successful for user: {username}")
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            logger.warning(f"Login failed: Invalid credentials for user: {username}")
            return jsonify({"msg": "Invalid username or password"}), 401

    @bot_routes.route('/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify(access_token=access_token), 200

    @bot_routes.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    @bot_routes.route('/dashboard', methods=['GET'])
    @jwt_required()
    def dashboard():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Fetch bot status
        settings = BotSettings.query.filter_by(user_id=user.id).first()
        bot_status = 'Running' if settings and settings.is_active else 'Stopped'
        
        # Fetch recent activities
        activities = BotActivity.get_recent_activities(user.id, 5)
        
        # Fetch projects
        projects = Project.query.filter_by(user_id=user.id).all()
        
        # Use the global EARNINGS_DATA for now
        earnings_data = EARNINGS_DATA
        
        dashboard_data = {
            "botStatus": bot_status,
            "recentActivities": [activity.to_dict() for activity in activities],
            "projects": [project.to_dict() for project in projects],
            "earnings": earnings_data,
            "userStats": {
                "totalTasksCompleted": user.total_tasks_completed,
                "totalRewardsEarned": user.total_rewards_earned,
                "currentStreak": user.current_streak
            },
            "settings": settings.to_dict() if settings else {}
        }
        
        return jsonify(dashboard_data), 200

    @bot_routes.route('/bot/initialize', methods=['POST'])
    @jwt_required()
    def initialize_bot_route():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_activity(user.id, "Bot Initialization", "Started", bot_type="Main")
        task = initialize_bot.delay()
        result = task.get()  # Wait for the task to complete
        log_activity(user.id, "Bot Initialization", result['message'], bot_type="Main")
        
        return jsonify(result), 200 if result['status'] == 'success' else 500

    @bot_routes.route('/bot/start/<routine>', methods=['POST'])
    @jwt_required()
    def start_routine_route(routine):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_activity(user.id, f"Start Routine", f"Starting {routine}")
        task = start_routine.delay(routine)
        result = task.get()  # Wait for the task to complete
        log_activity(user.id, f"Start Routine", result['message'])
        
        return jsonify(result), 200 if result['status'] == 'success' else 500

    @bot_routes.route('/bot/stop/<routine>', methods=['POST'])
    @jwt_required()
    def stop_routine_route(routine):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_activity(user.id, f"Stop Routine", f"Stopping {routine}")
        task = stop_routine.delay(routine)
        result = task.get()  # Wait for the task to complete
        log_activity(user.id, f"Stop Routine", result['message'])
        
        return jsonify(result), 200 if result['status'] == 'success' else 500

    @bot_routes.route('/bot/stop', methods=['POST'])
    @jwt_required()
    def stop_bot_route():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_activity(user.id, "Stop Bot", "Stopping bot")
        task = stop_bot.delay()
        result = task.get()  # Wait for the task to complete
        log_activity(user.id, "Stop Bot", result['message'])
        
        return jsonify(result), 200 if result['status'] == 'success' else 500

    @bot_routes.route('/bot/status', methods=['GET'])
    @jwt_required()
    def get_bot_status_route():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        task = get_bot_status.delay()
        result = task.get()  # Wait for the task to complete
        return jsonify(result), 200

    @bot_routes.route('/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        stats = tasks.update_statistics.delay(user.id).get()
        activities = BotActivity.get_recent_activities(user.id, 5)
        stats['activityLogs'] = activities
        return jsonify(stats)

    @bot_routes.route('/check_users', methods=['GET'])
    def check_users():
        users = User.query.all()
        user_list = [user.to_dict() for user in users]
        logger.info(f"Total users in database: {len(user_list)}")
        return jsonify({"users": user_list}), 200

    @bot_routes.route('/projects', methods=['GET'])
    @jwt_required()
    def get_projects():
        # Your code to get projects
        pass  # Replace this with your actual code

    @bot_routes.route('/projects/settings', methods=['GET', 'POST'])
    @jwt_required()
    def project_settings():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if request.method == 'GET':
            settings = BotSettings.get_by_user_id(user.id)
            return jsonify(settings.to_dict() if settings else {}), 200
        
        elif request.method == 'POST':
            data = request.get_json()
            BotSettings.create_or_update(
                user_id=user.id,
                is_active=data.get('is_active', False),
                run_interval=data.get('run_interval', 60),
                max_daily_runs=data.get('max_daily_runs', 5)
            )
            return jsonify({"message": "Settings updated successfully"}), 200

    @bot_routes.route('/earnings', methods=['GET'])
    @jwt_required()
    def get_earnings():
        # Modify the EARNINGS_DATA structure to match what the frontend expects
        formatted_earnings = {
            "total": EARNINGS_DATA["total"],
            "lastMonth": EARNINGS_DATA["lastMonth"],
            "history": EARNINGS_DATA["history"]
        }
        return jsonify(formatted_earnings), 200

    @bot_routes.route('/bot/stats', methods=['GET'])
    @jwt_required()
    def get_bot_stats():
        user_id = get_jwt_identity()
        stats = BotStatistics.query.filter_by(user_id=user_id).first()
        if stats:
            return jsonify({
                "tasks_completed": stats.tasks_completed,
                "rewards_earned": stats.rewards_earned,
                "streak": stats.streak,
                "total_runtime": stats.total_runtime,
                "errors_encountered": stats.errors_encountered
            }), 200
        else:
            return jsonify({"message": "No statistics found"}), 404

    @bot_routes.route('/verify_token', methods=['GET'])
    @jwt_required()
    def verify_token():
        current_user = get_jwt_identity()
        return jsonify({"msg": "Token is valid", "user": current_user}), 200

    @bot_routes.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return resp, 200

    @bot_routes.route('/user/profile', methods=['GET'])
    @jwt_required()
    def get_user_profile():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200

    @bot_routes.route('/user/profile', methods=['PUT'])
    @jwt_required()
    def update_user_profile():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        if 'email' in data:
            user.email = data['email']
        # Add more fields as needed
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    @bot_routes.route('/bot/start_recorded/<routine>', methods=['POST'])
    @jwt_required()
    def start_recorded_routine_route(routine):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_activity(user.id, f"Start Recorded Routine", f"Starting {routine}")
        task = playback_routine.delay(routine)
        result = task.get()  # Wait for the task to complete
        log_activity(user.id, f"Start Recorded Routine", result['message'])
        
        return jsonify(result), 200 if result['status'] == 'success' else 500

    @bot_routes.route('/bot/start_recording', methods=['POST'])
    @jwt_required()
    def start_recording():
        try:
            data = request.get_json()
            url = data.get('url', 'https://web.telegram.org/k/')
            message = recorder.start_recording(url)
            return jsonify({"message": message}), 200
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            return jsonify({"error": "Failed to start recording", "details": str(e)}), 500

    @bot_routes.route('/bot/stop_recording', methods=['POST'])
    @jwt_required()
    def stop_recording():
        try:
            data = request.get_json()
            routine_name = data.get('routine_name')
            if not routine_name:
                return jsonify({"error": "Routine name is required"}), 400
            message = recorder.stop_recording(routine_name)
            return jsonify({"message": message}), 200
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            return jsonify({"error": "Failed to stop recording", "details": str(e)}), 500

    @bot_routes.route('/bot/recorded_routines', methods=['GET'])
    @jwt_required()
    def list_recorded_routines():
        routines = get_recorded_routines()
        return jsonify({"routines": routines}), 200

    @bot_routes.route('/bot/refresh_routines', methods=['GET'])
    @jwt_required()
    def refresh_recorded_routines():
        routines = get_recorded_routines()
        return jsonify({"routines": routines}), 200

    @bot_routes.route('/bot/delete_routine/<routine_name>', methods=['DELETE'])
    @jwt_required()
    def delete_recorded_routine(routine_name):
        file_name = f'{routine_name}_actions.json'
        file_path = os.path.join(RECORDED_ROUTINES_DIR, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"Routine {routine_name} deleted successfully"}), 200
        else:
            return jsonify({"error": f"Routine {routine_name} not found"}), 404

    app.register_blueprint(bot_routes, url_prefix='/api')

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        logger.info(f"Registration attempt for username: {username}, email: {email}")

        if not username or not email or not password:
            logger.warning("Registration attempt with missing data")
            return jsonify({'message': 'Missing required fields'}), 400

        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration failed: Username {username} already exists")
            return jsonify({'message': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed: Email {email} already exists")
            return jsonify({'message': 'Email already exists'}), 400

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            logger.info(f"User registered successfully: {username}")
            return jsonify({'message': 'User registered successfully'}), 201
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return jsonify({'message': 'An error occurred during registration'}), 500