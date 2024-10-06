from extensions import celery, db
from bot.routines.goats import GOATSRoutine
from models.models import BotActivity, User, AirdropProject
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task
def run_goats_routine(user_id, project_id, settings):
    logger.info(f"Starting GOATS routine for user {user_id} on project {project_id}")
    try:
        routine = GOATSRoutine(settings)
        result = routine.run()
        
        # Log the activity
        user = User.query.get(user_id)
        project = AirdropProject.query.get(project_id)
        activity = BotActivity(user_id=user_id, project_id=project_id, action='run', details=str(result))
        db.session.add(activity)
        db.session.commit()
        
        logger.info("GOATS routine completed successfully")
        return {"status": "success", "message": "GOATS routine completed", "result": result}
    except Exception as e:
        logger.error(f"Error in GOATS routine: {str(e)}")
        
        # Log the error
        activity = BotActivity(user_id=user_id, project_id=project_id, action='error', details=str(e))
        db.session.add(activity)
        db.session.commit()
        
        return {"status": "error", "message": str(e)}

# You can add more tasks for other routines (1Win, PX) here