from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from backend.celery_config import celery_app as celery
from backend.tasks import initialize_bot, start_routine, stop_routine, stop_bot, get_bot_status
from backend.models import db  # Import db from models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    @app.route('/api/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        
        data = request.json
        # Here you would typically add the user to your database
        # For now, we'll just return a success message
        return jsonify({"message": "User registered successfully in Flask backend"}), 201

    @app.route('/api/dashboard', methods=['GET'])
    def dashboard():
        logger.info("Dashboard route accessed")
        token = request.headers.get('Authorization', '').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                print("Unauthorized access attempt")  # Add this line
                return jsonify({"error": "Unauthorized"}), 401
            print(f"Authorized access for user: {user}")  # Add this line
        except Exception as e:
            print(f"Error in dashboard route: {str(e)}")  # Add this line
            return jsonify({"error": str(e)}), 401
        
        bot_status = get_bot_status.delay().get()
        dashboard_data = {
            "botStatus": bot_status['status'],
            "userStats": {
                "totalTasksCompleted": 100,
                "totalRewardsEarned": 500,
                "currentStreak": 5
            },
            "recentActivities": [
                {"action": "Task Completed", "result": "Earned 10 points"},
                {"action": "Bot Started", "result": "Successfully initialized"}
            ]
        }
        print(f"Returning dashboard data: {dashboard_data}")  # Add this line
        return jsonify(dashboard_data)

    @app.route('/api/bot/initialize', methods=['POST'])
    def initialize_bot_route():
        token = request.headers.get('Authorization').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        task = initialize_bot.delay()
        return jsonify({"message": "Bot initialization started", "task_id": task.id}), 202

    @app.route('/api/bot/start/<routine>', methods=['POST'])
    def start_routine_route(routine):
        token = request.headers.get('Authorization').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        task = start_routine.delay(routine)
        return jsonify({"message": f"Starting {routine} routine", "task_id": task.id}), 202

    @app.route('/api/bot/stop/<routine>', methods=['POST'])
    def stop_routine_route(routine):
        token = request.headers.get('Authorization').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        task = stop_routine.delay(routine)
        return jsonify({"message": f"Stopping {routine} routine", "task_id": task.id}), 202

    @app.route('/api/bot/stop', methods=['POST'])
    def stop_bot_route():
        token = request.headers.get('Authorization').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        task = stop_bot.delay()
        return jsonify({"message": "Stopping bot", "task_id": task.id}), 202

    @app.route('/api/bot/status', methods=['GET'])
    def bot_status_route():
        token = request.headers.get('Authorization').split(' ')[1]
        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401

        status = get_bot_status.delay().get()
        return jsonify(status)

    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Flask app created and running")
    app.run(debug=True)