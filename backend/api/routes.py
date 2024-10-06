from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models.models import User, BotConfig, AirdropProject
from app import db, celery
from celery_tasks.tasks import run_goats_routine

api_bp = Blueprint('api', __name__)

@api_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@api_bp.route('/bot/start', methods=['POST'])
@jwt_required()
def start_bot():
    current_user = get_jwt_identity()
    project_id = request.json.get('project_id')
    user = User.query.filter_by(username=current_user).first()
    config = BotConfig.query.filter_by(user_id=user.id, project_id=project_id).first()
    
    if not config:
        return jsonify({"msg": "Bot configuration not found"}), 404
    
    # Start the bot task
    task = run_goats_routine.delay(config.settings)
    
    return jsonify({"msg": "Bot started", "task_id": task.id}), 202

@api_bp.route('/bot/stop', methods=['POST'])
@jwt_required()
def stop_bot():
    current_user = get_jwt_identity()
    project_id = request.json.get('project_id')
    
    # For now, we'll just return a success message
    # In the future, implement actual bot stopping logic
    return jsonify({"msg": "Bot stopped"}), 200

@api_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    projects = AirdropProject.query.filter_by(is_active=True).all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description} for p in projects]), 200

@api_bp.route('/bot/config', methods=['GET', 'POST'])
@jwt_required()
def bot_config():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if request.method == 'GET':
        configs = BotConfig.query.filter_by(user_id=user.id).all()
        return jsonify([{
            "project_id": c.project_id,
            "is_active": c.is_active,
            "settings": c.settings
        } for c in configs]), 200
    
    elif request.method == 'POST':
        project_id = request.json.get('project_id')
        is_active = request.json.get('is_active')
        settings = request.json.get('settings')
        
        config = BotConfig.query.filter_by(user_id=user.id, project_id=project_id).first()
        if not config:
            config = BotConfig(user_id=user.id, project_id=project_id)
        
        config.is_active = is_active
        config.settings = settings
        db.session.add(config)
        db.session.commit()
        
        return jsonify({"msg": "Bot configuration updated"}), 200
