from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, BotSettings, BotActivity, Project, BotStatistics
from extensions import db
from celery_tasks.tasks import run_goats_bot, update_statistics, start_bot_task, stop_bot_task
import random
from datetime import datetime, timedelta
import logging

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

def init_routes(app):
    bot_routes = Blueprint('bot_routes', __name__)
    
    @bot_routes.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        logger.debug(f"Received registration request: username={username}, email={email}")

        if not username or not password or not email:
            logger.warning("Registration failed: Missing username, password, or email")
            return jsonify({"msg": "Missing username, password, or email"}), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logger.warning(f"Registration failed: Username {username} already exists")
            return jsonify({"msg": "Username already exists"}), 400

        try:
            user_id = User.create(username, password, email)
            logger.info(f"User registered successfully: username={username}, user_id={user_id}")
            return jsonify({"msg": "User created successfully", "user_id": user_id}), 201
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return jsonify({"msg": "An error occurred during registration"}), 500

    @bot_routes.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        logger.debug(f"Login attempt for username: {username}")

        if not username or not password:
            logger.warning("Login attempt with missing username or password")
            return jsonify({"msg": "Missing username or password"}), 400

        try:
            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password_hash, password):
                logger.warning(f"Login failed: Invalid credentials for user: {username}")
                return jsonify({"msg": "Invalid username or password"}), 401

            logger.info(f"Login successful for user: {username}")
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            return jsonify({"msg": "An error occurred during login"}), 500

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

    @bot_routes.route('/bot/start', methods=['POST'])
    @jwt_required()
    def start_bot():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        task = start_bot_task.delay()
        return jsonify({"message": "Bot started", "task_id": str(task.id)}), 202

    @bot_routes.route('/bot/stop', methods=['POST'])
    @jwt_required()
    def stop_bot():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        task = stop_bot_task.delay()
        return jsonify({"message": "Bot stop requested", "task_id": str(task.id)}), 202

    @bot_routes.route('/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        stats = update_statistics.delay(user.id).get()
        activities = BotActivity.get_recent_activities(user.id, 5)
        stats['activityLogs'] = activities
        return jsonify(stats)

    @bot_routes.route('/check_users', methods=['GET'])
    def check_users():
        users = User.query.all()
        user_list = [user.to_dict() for user in users]
        logger.info(f"Total users in database: {len(user_list)}")
        return jsonify({"users": user_list}), 200

    @bot_routes.route('/projects', methods=['GET', 'POST'])
    @jwt_required()
    def projects():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if request.method == 'POST':
            data = request.get_json()
            new_project = Project(
                name=data['name'],
                user_id=user.id,
                enabled=data.get('enabled', True),
                interval=data.get('interval', 60),
                max_daily_runs=data.get('max_daily_runs', 5)
            )
            db.session.add(new_project)
            db.session.commit()
            return jsonify(new_project.to_dict()), 201
        
        projects = Project.query.filter_by(user_id=user.id).all()
        return jsonify([project.to_dict() for project in projects]), 200

    @bot_routes.route('/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
    @jwt_required()
    def project(project_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        project = Project.query.filter_by(id=project_id, user_id=user.id).first_or_404()
        
        if request.method == 'GET':
            return jsonify(project.to_dict()), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            project.name = data.get('name', project.name)
            project.enabled = data.get('enabled', project.enabled)
            project.interval = data.get('interval', project.interval)
            project.max_daily_runs = data.get('max_daily_runs', project.max_daily_runs)
            db.session.commit()
            return jsonify(project.to_dict()), 200
        
        elif request.method == 'DELETE':
            db.session.delete(project)
            db.session.commit()
            return '', 204

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

    @bot_routes.route('/projects/settings', methods=['GET', 'POST'])
    @jwt_required()
    def project_settings():
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if request.method == 'GET':
            settings = BotSettings.query.filter_by(user_id=user.id).first()
            return jsonify(settings.to_dict() if settings else {}), 200
        
        elif request.method == 'POST':
            data = request.get_json()
            BotSettings.create_or_update(
                user_id=user.id,
                is_active=data.get('is_active', False),
                run_interval=data.get('run_interval', 60),
                max_daily_runs=data.get('max_daily_runs', 5)
            )
            return jsonify({"msg": "Settings updated successfully"}), 200

    @bot_routes.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        # Here you would typically blacklist the token
        # For now, we'll just log the logout attempt
        current_user = get_jwt_identity()
        logger.info(f"Logout attempt for user: {current_user}")
        return jsonify({"msg": "Successfully logged out"}), 200

    @bot_routes.route('/verify_token', methods=['GET'])
    @jwt_required()
    def verify_token():
        current_user = get_jwt_identity()
        return jsonify({"msg": "Token is valid", "user": current_user}), 200

    app.register_blueprint(bot_routes, url_prefix='/api')