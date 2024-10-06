from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, BotSettings, BotActivity, Project
from celery_tasks.tasks import run_goats_bot, update_statistics
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

        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        existing_user = User.get_by_username(username)
        if existing_user:
            return jsonify({"msg": "Username already exists"}), 400

        hashed_password = generate_password_hash(password)
        user_id = User.create(username, hashed_password, email)

        return jsonify({"msg": "User created successfully", "user_id": user_id}), 201

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
            user = User.get_by_username(username)

            if not user:
                logger.warning(f"Login failed: User not found for username: {username}")
                return jsonify({"msg": "Invalid username or password"}), 401

            if check_password_hash(user.password_hash, password):
                logger.info(f"Login successful for user: {username}")
                access_token = create_access_token(identity=username)
                return jsonify(access_token=access_token), 200
            else:
                logger.warning(f"Login failed: Invalid password for user: {username}")
                return jsonify({"msg": "Invalid username or password"}), 401
        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            return jsonify({"msg": "An error occurred during login"}), 500

    @bot_routes.route('/bot/status', methods=['GET'])
    @jwt_required()
    def bot_status():
        current_user = get_jwt_identity()
        user = User.get_by_username(current_user)
        settings = BotSettings.get_by_user_id(user['id'])
        status = 'Running' if settings and settings['is_active'] else 'Stopped'
        return jsonify({"status": status}), 200

    @bot_routes.route('/bot/start', methods=['POST'])
    @jwt_required()
    def start_bot():
        current_user = get_jwt_identity()
        user = User.get_by_username(current_user)
        bot_name = request.json.get('bot_name', 'goats')
        
        # Check if the bot is already running
        settings = BotSettings.get_by_user_id(user.id)
        if settings and settings.is_active:
            return jsonify({"message": f"{bot_name} bot is already running"}), 200
        
        if bot_name == 'goats':
            task = run_goats_bot.delay(user.id)
            BotSettings.create_or_update(user.id, True, 60, 5)  # Example values
            return jsonify({"message": f"{bot_name} bot started", "task_id": str(task.id)})
        else:
            return jsonify({"error": "Invalid bot name"}), 400

    @bot_routes.route('/bot/stop', methods=['POST'])
    @jwt_required()
    def stop_bot():
        current_user = get_jwt_identity()
        user = User.get_by_username(current_user)
        bot_name = request.json.get('bot_name', 'goats')
        BotSettings.create_or_update(user.id, False, 60, 5)  # Example values
        return jsonify({"message": f"{bot_name} bot stopped"})

    @bot_routes.route('/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        current_user = get_jwt_identity()
        user = User.get_by_username(current_user)
        stats = update_statistics.delay(user['id']).get()
        activities = BotActivity.get_recent_activities(user['id'], 5)
        stats['activityLogs'] = activities
        return jsonify(stats)

    @bot_routes.route('/dashboard', methods=['GET'])
    @jwt_required()
    def dashboard():
        current_user = get_jwt_identity()
        user = User.get_by_username(current_user)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Fetch bot status
        settings = BotSettings.get_by_user_id(user.id)
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
        user = User.get_by_username(current_user)
        
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
        user = User.get_by_username(current_user)
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

    app.register_blueprint(bot_routes, url_prefix='/api')