from celery import shared_task
from models import User, BotSettings, BotActivity
from bot.routines.goats import GoatsBot
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_goats_bot(user_id):
    logger.info(f"Starting GOATS bot for user {user_id}")
    settings = BotSettings.get_by_user_id(user_id)
    bot = GoatsBot(settings)
    result = bot.run()
    
    # Log the activity
    BotActivity.log(user_id, 'goats', 'run', result['status'], result['message'])
    
    # Update statistics
    stats = bot.get_statistics()
    User.update_statistics(user_id, stats['tasks_completed'], stats['rewards_earned'], stats['streak'])
    
    logger.info(f"GOATS bot completed for user {user_id}: {result}")
    return result

@shared_task
def update_statistics(user_id):
    logger.info(f"Updating statistics for user {user_id}")
    user = User.get_by_username(user_id)
    if user:
        stats = {
            "total_tasks_completed": user.total_tasks_completed,
            "total_rewards_earned": user.total_rewards_earned,
            "current_streak": user.current_streak
        }
    else:
        stats = {
            "total_tasks_completed": 0,
            "total_rewards_earned": 0,
            "current_streak": 0
        }
    return stats