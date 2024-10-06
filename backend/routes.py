from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, User, Project
from datetime import datetime, timedelta
import random

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
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        db = next(get_db())
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return jsonify({"msg": "Username already exists"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()

        if user and check_password_hash(user.hashed_password, password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Invalid username or password"}), 401

    @app.route('/api/bot/status', methods=['GET'])
    @jwt_required()
    def bot_status():
        # Placeholder: In a real application, you'd check the actual status of the bot
        statuses = ['running', 'stopped', 'paused']
        return jsonify({"status": random.choice(statuses)}), 200

    @app.route('/api/bot/start', methods=['POST'])
    @jwt_required()
    def start_bot():
        # Placeholder: In a real application, you'd actually start the bot
        return jsonify({"message": "Bot started successfully"}), 200

    @app.route('/api/bot/stop', methods=['POST'])
    @jwt_required()
    def stop_bot():
        # Placeholder: In a real application, you'd actually stop the bot
        return jsonify({"message": "Bot stopped successfully"}), 200

    @app.route('/api/projects', methods=['GET'])
    @jwt_required()
    def get_projects():
        db = next(get_db())
        current_user = get_jwt_identity()
        user = db.query(User).filter(User.username == current_user).first()
        projects = db.query(Project).filter(Project.user_id == user.id).all()
        return jsonify([project.to_dict() for project in projects]), 200

    @app.route('/api/projects/settings', methods=['GET'])
    @jwt_required()
    def get_project_settings():
        # Placeholder: Return some dummy project settings
        settings = [
            {
                "id": "1",
                "name": "Project 1",
                "enabled": True,
                "interval": 30,
                "maxDailyRuns": 5
            },
            {
                "id": "2",
                "name": "Project 2",
                "enabled": False,
                "interval": 60,
                "maxDailyRuns": 3
            }
        ]
        return jsonify(settings), 200

    @app.route('/api/dashboard', methods=['GET'])
    @jwt_required()
    def get_dashboard_data():
        return jsonify({
            "totalEarnings": EARNINGS_DATA["total"],
            "lastMonthEarnings": EARNINGS_DATA["lastMonth"],
            "activeProjects": random.randint(1, 5),
            "runningBots": random.randint(0, 3)
        }), 200

    @app.route('/api/earnings', methods=['GET'])
    @jwt_required()
    def get_earnings():
        return jsonify(EARNINGS_DATA["history"]), 200

    @app.route('/api/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        stats = {
            "totalRuns": random.randint(100, 1000),
            "successRate": round(random.uniform(0.7, 0.99), 2),
            "averageEarningsPerRun": round(EARNINGS_DATA["total"] / 100, 2),  # Assuming 100 runs for simplicity
            "totalEarnings": EARNINGS_DATA["total"],
            "activityLogs": [
                {"id": i, "timestamp": datetime.now().isoformat(), "action": f"Action {i}"} 
                for i in range(5)
            ]
        }
        return jsonify(stats), 200

    @app.route('/api/settings', methods=['GET'])
    @jwt_required()
    def get_settings():
        # Placeholder: Return some dummy user settings
        settings = {
            "theme": "dark",
            "language": "en",
            "emailNotifications": True
        }
        return jsonify(settings), 200

    @app.route('/api/settings', methods=['PUT'])
    @jwt_required()
    def update_settings():
        data = request.get_json()
        # Placeholder: In a real application, you'd update the user's settings in the database
        return jsonify({"message": "Settings updated successfully"}), 200

    # Error handler for JWT authentication errors
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"msg": "Unauthorized access"}), 401

    # Error handler for other exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error here (you can use app.logger)
        return jsonify({"msg": "An unexpected error occurred"}), 500