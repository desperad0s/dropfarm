from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Project, Bot, ActivityLog
from datetime import datetime, timedelta

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@api.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    return jsonify([project.to_dict() for project in projects]), 200

@api.route('/bot/start/<int:project_id>', methods=['POST'])
@jwt_required()
def start_bot(project_id):
    bot = Bot.query.filter_by(project_id=project_id).first()
    if bot:
        bot.status = 'active'
        db.session.commit()
        return jsonify({"msg": "Bot started successfully"}), 200
    return jsonify({"msg": "Bot not found"}), 404

@api.route('/bot/stop/<int:project_id>', methods=['POST'])
@jwt_required()
def stop_bot(project_id):
    bot = Bot.query.filter_by(project_id=project_id).first()
    if bot:
        bot.status = 'inactive'
        db.session.commit()
        return jsonify({"msg": "Bot stopped successfully"}), 200
    return jsonify({"msg": "Bot not found"}), 404

@api.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    total_earnings = sum(project.earnings for project in projects)
    active_bots = sum(1 for project in projects if project.bot.status == 'active')
    recent_activities = ActivityLog.query.filter(
        ActivityLog.user_id == user.id,
        ActivityLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    return jsonify({
        "projects": [project.to_dict() for project in projects],
        "total_earnings": total_earnings,
        "active_bots": active_bots,
        "recent_activities": recent_activities
    }), 200

@api.route('/earnings', methods=['GET'])
@jwt_required()
def get_earnings_data():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    # Calculate earnings for the past week
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    earnings_data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        daily_earnings = sum(
            project.calculate_daily_earnings(date) for project in projects
        )
        earnings_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "earnings": daily_earnings
        })
    
    return jsonify(earnings_data), 200

@api.route('/bot/status', methods=['GET'])
@jwt_required()
def get_bot_status():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    bots = Bot.query.join(Project).filter(Project.user_id == user.id).all()
    
    return jsonify({
        "status": "active" if any(bot.status == 'active' for bot in bots) else "inactive"
    }), 200

@api.route('/projects/settings', methods=['GET'])
@jwt_required()
def get_project_settings():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    return jsonify([project.to_dict() for project in projects]), 200

@api.route('/projects/<int:project_id>/settings', methods=['PUT'])
@jwt_required()
def update_project_settings(project_id):
    data = request.get_json()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    for key, value in data.items():
        setattr(project, key, value)
    
    db.session.commit()
    return jsonify(project.to_dict()), 200

@api.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    # Calculate various statistics
    total_earnings = sum(project.earnings for project in projects)
    active_projects = sum(1 for project in projects if project.bot.status == 'active')
    total_projects = len(projects)
    
    # Get activity logs
    logs = ActivityLog.query.filter_by(user_id=user.id).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    return jsonify({
        "total_earnings": total_earnings,
        "active_projects": active_projects,
        "total_projects": total_projects,
        "activity_logs": [log.to_dict() for log in logs]
    }), 200

@api.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    return jsonify(user.settings.to_dict()), 200

@api.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    for key, value in data.items():
        setattr(user.settings, key, value)
    
    db.session.commit()
    return jsonify(user.settings.to_dict()), 200