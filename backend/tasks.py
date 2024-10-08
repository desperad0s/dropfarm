import asyncio
from pyppeteer import launch
from backend.celery_app import celery_app
import logging
import os
import json
from backend.extensions import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a path for user data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')

# Define a path for recorded routines
RECORDED_ROUTINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_routines')

# Global variable to store the browser instance
browser = None
bot_status = 'stopped'
active_routines = set()

@celery_app.task(name='backend.tasks.initialize_bot')
async def initialize_bot():
    global browser, bot_status
    if browser:
        return {'status': 'success', 'message': 'Bot already initialized', 'bot_status': bot_status}

    try:
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox'],
            userDataDir=USER_DATA_DIR
        )
        page = await browser.newPage()
        await page.goto('https://web.telegram.org/k/')
        logger.info("Navigated to Telegram Web")

        # Wait for the page to load (adjust timeout as needed)
        await page.waitForSelector('body', {'timeout': 30000})
        logger.info("Page loaded successfully")

        # Check if we're already logged in
        if 'tgme_logo_wrap' not in await page.content():
            logger.info("User is already logged in")
            bot_status = 'initialized'
            return {'status': 'success', 'message': 'Bot initialized and logged into Telegram', 'bot_status': bot_status}
        else:
            logger.info("Login required")
            bot_status = 'initialized'
            return {'status': 'success', 'message': 'Bot initialized, Telegram login required', 'bot_status': bot_status}

    except Exception as e:
        logger.error(f"Error initializing bot: {str(e)}")
        bot_status = 'error'
        return {'status': 'error', 'message': f'Error initializing bot: {str(e)}', 'bot_status': bot_status}

@celery_app.task(name='backend.tasks.playback_routine')
async def playback_routine(routine_name):
    global browser, bot_status, active_routines
    if not browser:
        initialize_result = await initialize_bot()
        if initialize_result['status'] != 'success':
            return initialize_result
    
    try:
        page = await browser.newPage()
        await page.bringToFront()
        logger.info(f"Starting playback of routine: {routine_name}")
        
        file_path = os.path.join(RECORDED_ROUTINES_DIR, f'{routine_name}_actions.json')
        logger.info(f"Attempting to open file: {file_path}")
        
        with open(file_path, 'r') as f:
            recorded_data = json.load(f)
        
        logger.info(f"Loaded data: {recorded_data}")
        
        actions = recorded_data['actions']
        
        logger.info(f"Number of actions to perform: {len(actions)}")
        
        for index, action in enumerate(actions):
            logger.info(f"Performing action {index + 1}/{len(actions)}: {action}")
            
            try:
                if action['type'] == 'click':
                    if 'selector' in action:
                        await page.click(action['selector'])
                    else:
                        await page.mouse.click(action['x'], action['y'])
                elif action['type'] == 'input':
                    await page.type(action['selector'], action['value'])
                elif action['type'] == 'wait':
                    await asyncio.sleep(action['duration'])
                elif action['type'] == 'navigate':
                    await page.goto(action['url'])
                else:
                    logger.warning(f"Unknown action type: {action['type']}")
            except Exception as e:
                logger.error(f"Error performing action {index + 1}: {action['type']}. Error: {str(e)}")
            
            await asyncio.sleep(0.1)  # Small delay between actions
        
        active_routines.add(routine_name)
        bot_status = 'running'
        logger.info(f"Routine {routine_name} completed successfully")
        return {'status': 'success', 'message': f'{routine_name} routine completed'}
    except Exception as e:
        logger.error(f"Error in {routine_name} routine: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='backend.tasks.start_routine')
def start_routine(routine_name):
    global bot_status, active_routines
    if not browser:
        return {'status': 'error', 'message': 'Bot not initialized'}
    
    active_routines.add(routine_name)
    bot_status = 'running'
    
    # Implement routine logic here
    logger.info(f"Starting {routine_name} routine")
    
    return {'status': 'success', 'message': f'{routine_name} routine started'}

@celery_app.task(name='backend.tasks.stop_routine')
def stop_routine(routine_name):
    global bot_status, active_routines
    if routine_name in active_routines:
        active_routines.remove(routine_name)
    
    if not active_routines:
        bot_status = 'initialized'
    else:
        bot_status = 'running'
    
    return {'status': 'success', 'message': f'{routine_name} routine stopped'}

@celery_app.task(name='backend.tasks.stop_bot')
async def stop_bot():
    global browser, bot_status, active_routines
    if browser:
        await browser.close()
        browser = None
    bot_status = 'stopped'
    active_routines.clear()
    return {'status': 'success', 'message': 'Bot stopped and deinitialized', 'bot_status': bot_status}

@celery_app.task(name='backend.tasks.get_bot_status')
def get_bot_status():
    return {'status': bot_status, 'active_routines': list(active_routines)}