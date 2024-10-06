from app import celery, logger
from models import User, BotConfig, AirdropProject
from bot.routines import GOATSRoutine, OneWinRoutine, PXRoutine

@celery.task
def start_bot(username, project_id):
    logger.info(f"Starting bot for user {username} on project {project_id}")
    user = User.query.filter_by(username=username).first()
    project = AirdropProject.query.get(project_id)
    config = BotConfig.query.filter_by(user_id=user.id, project_id=project_id).first()
    
    if not config or not config.is_active:
        logger.warning(f"Bot not configured or inactive for user {username} on project {project_id}")
        return
    
    routine = get_routine(project.name, config.settings)
    if routine:
        routine.run()
    else:
        logger.error(f"Unknown project: {project.name}")

@celery.task
def stop_bot(username, project_id):
    logger.info(f"Stopping bot for user {username} on project {project_id}")
    # Implement bot stopping logic here

def get_routine(project_name, settings):
    if project_name == "GOATS":
        return GOATSRoutine(settings)
    elif project_name == "1Win":
        return OneWinRoutine(settings)
    elif project_name == "PX":
        return PXRoutine(settings)
    return None