from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import logging
from celery import Celery

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Celery
celery = Celery(__name__, broker='redis://localhost:6379/0')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Use your actual database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure random key
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    db.init_app(app)
    celery.conf.update(app.config)

    logging.basicConfig(level=logging.INFO)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(255), nullable=False)

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "User already exists"}), 409
        user = User(email=data['email'], password=data['password'])  # In production, hash the password
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user and user.password == data['password']:  # In production, use proper password hashing
            access_token = create_access_token(identity=user.email)
            return jsonify(access_token=access_token), 200
        return jsonify({"message": "Invalid credentials"}), 401

    @app.route('/api/dashboard', methods=['GET'])
    @jwt_required()
    def dashboard():
        current_user = get_jwt_identity()
        # Fetch actual data from database
        return jsonify({
            "botStatus": "Running",
            "userStats": {
                "totalTasksCompleted": 100,
                "totalRewardsEarned": 500,
                "currentStreak": 5
            },
            "recentActivities": [
                {"action": "Task Completed", "result": "Earned 10 points"},
                {"action": "Bot Started", "result": "Successfully initialized"}
            ]
        })

    @app.route('/api/bot/initialize', methods=['POST'])
    @jwt_required()
    def initialize_bot():
        # Implement bot initialization logic
        celery.send_task('tasks.initialize_bot')
        return jsonify({"message": "Bot initialization started", "status": "success"})

    @app.route('/api/bot/start/<routine>', methods=['POST'])
    @jwt_required()
    def start_routine(routine):
        # Implement routine start logic
        celery.send_task('tasks.start_routine', args=[routine])
        return jsonify({"message": f"{routine} routine start initiated"})

    @app.route('/api/bot/stop/<routine>', methods=['POST'])
    @jwt_required()
    def stop_routine(routine):
        # Implement routine stop logic
        celery.send_task('tasks.stop_routine', args=[routine])
        return jsonify({"message": f"{routine} routine stop initiated"})

    @app.route('/api/bot/stop', methods=['POST'])
    @jwt_required()
    def stop_bot():
        # Implement bot stop logic
        celery.send_task('tasks.stop_bot')
        return jsonify({"message": "Bot stop initiated"})

    @app.route('/api/bot/status', methods=['GET'])
    @jwt_required()
    def bot_status():
        # Implement bot status check logic
        # This should ideally fetch the status from a database or a shared state
        return jsonify({"status": "running", "active_routines": ["goats", "onewin"]})

    @app.route('/api/bot/start_recording', methods=['POST'])
    @jwt_required()
    def start_recording():
        # Implement start recording logic
        return jsonify({"message": "Recording started successfully"})

    @app.route('/api/bot/stop_recording', methods=['POST'])
    @jwt_required()
    def stop_recording():
        # Implement stop recording logic
        return jsonify({"message": "Recording stopped and saved successfully"})

    @app.route('/api/bot/recorded_routines', methods=['GET'])
    @jwt_required()
    def get_recorded_routines():
        try:
            # Implement get recorded routines logic
            # For now, we'll return dummy data
            routines = ["goats", "onewin", "px"]
            return jsonify(routines), 200
        except Exception as e:
            app.logger.error(f"Error fetching recorded routines: {str(e)}")
            return jsonify({"error": "Failed to fetch recorded routines"}), 500

    @app.route('/api/bot/recorded_routines/<routine_name>', methods=['DELETE'])
    @jwt_required()
    def delete_recorded_routine(routine_name):
        # Implement delete recorded routine logic
        return jsonify({"message": f"Routine {routine_name} deleted successfully"})

    @app.route('/api/bot/refresh_recorded_routines', methods=['GET'])
    @jwt_required()
    def refresh_recorded_routines():
        # Implement refresh recorded routines logic
        return jsonify(["goats", "onewin", "px"])

    @app.route('/api/bot/start_recorded/<routine_name>', methods=['POST'])
    @jwt_required()
    def start_recorded_routine(routine_name):
        # Implement start recorded routine logic
        return jsonify({"message": f"Recorded routine {routine_name} started successfully"})

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)