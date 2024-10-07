from backend.celery_app import celery_app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a path for user data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')

# Define a path for recorded routines
RECORDED_ROUTINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_routines')

# Global variable to store the WebDriver instance
driver = None
bot_status = 'stopped'
active_routines = set()

@celery_app.task(name='backend.tasks.initialize_bot')
def initialize_bot():
    global driver, bot_status
    if driver:
        return {'status': 'success', 'message': 'Bot already initialized'}

    chrome_options = Options()
    chrome_options.add_argument(f'user-data-dir={USER_DATA_DIR}')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver initialized successfully")

        # Navigate to Telegram Web
        driver.get('https://web.telegram.org/k/')
        logger.info("Navigated to Telegram Web")

        # Wait for the page to load (adjust timeout as needed)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        logger.info("Page loaded successfully")

        # Check if we're already logged in
        if 'tgme_logo_wrap' not in driver.page_source:
            logger.info("User is already logged in")
            bot_status = 'initialized'
            return {'status': 'success', 'message': 'Bot initialized and logged into Telegram'}
        else:
            logger.info("Login required")
            bot_status = 'initialized'
            return {'status': 'success', 'message': 'Bot initialized, Telegram login required'}

    except Exception as e:
        logger.error(f"Error initializing bot: {str(e)}")
        return {'status': 'error', 'message': f'Error initializing bot: {str(e)}'}

@celery_app.task(name='backend.tasks.playback_routine')
def playback_routine(routine_name):
    global driver, bot_status, active_routines
    if not driver:
        initialize_result = initialize_bot()
        if initialize_result['status'] != 'success':
            return initialize_result
    
    try:
        driver.execute_script("window.focus();")
        logger.info(f"Starting playback of routine: {routine_name}")
        
        file_path = os.path.join(RECORDED_ROUTINES_DIR, f'{routine_name}_actions.json')
        logger.info(f"Attempting to open file: {file_path}")
        
        with open(file_path, 'r') as f:
            recorded_data = json.load(f)
        
        logger.info(f"Loaded data: {recorded_data}")
        
        actions = recorded_data['actions']
        
        logger.info(f"Number of actions to perform: {len(actions)}")
        
        # Get the current window size
        window_size = driver.get_window_size()
        current_width = window_size['width']
        current_height = window_size['height']
        
        # Get the recorded window size (you need to add this to your recorder)
        recorded_width = recorded_data.get('window_width', current_width)
        recorded_height = recorded_data.get('window_height', current_height)
        
        # Calculate scaling factors
        width_scale = current_width / recorded_width
        height_scale = current_height / recorded_height
        
        for index, action in enumerate(actions):
            logger.info(f"Performing action {index + 1}/{len(actions)}: {action}")
            
            try:
                if action['type'] == 'click':
                    if 'selector' in action:
                        element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, action['selector']))
                        )
                        ActionChains(driver).move_to_element(element).click().perform()
                    else:
                        scaled_x = int(action['x'] * width_scale)
                        scaled_y = int(action['y'] * height_scale)
                        ActionChains(driver).move_by_offset(scaled_x, scaled_y).click().perform()
                    logger.info(f"Clicked at ({scaled_x}, {scaled_y})")
                elif action['type'] == 'input':
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, action['selector']))
                    )
                    element.clear()
                    element.send_keys(action['value'])
                    logger.info(f"Input text to element: {action['selector']}")
                elif action['type'] == 'mousemove':
                    scaled_x = int(action['x'] * width_scale)
                    scaled_y = int(action['y'] * height_scale)
                    ActionChains(driver).move_by_offset(scaled_x, scaled_y).perform()
                    logger.info(f"Moved mouse to: ({scaled_x}, {scaled_y})")
                elif action['type'] == 'wait':
                    time.sleep(action['duration'])
                    logger.info(f"Waited for {action['duration']} seconds")
                elif action['type'] == 'navigate':
                    driver.get(action['url'])
                    logger.info(f"Navigated to: {action['url']}")
                else:
                    logger.warning(f"Unknown action type: {action['type']}")
            except Exception as e:
                logger.error(f"Error performing action {index + 1}: {action['type']}. Error: {str(e)}")
            
            time.sleep(0.1)  # Small delay between actions
        
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
    if not driver:
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
def stop_bot():
    global driver, bot_status, active_routines
    if driver:
        driver.quit()
        driver = None
    bot_status = 'stopped'
    active_routines.clear()
    return {'status': 'success', 'message': 'Bot stopped and deinitialized'}

@celery_app.task(name='backend.tasks.get_bot_status')
def get_bot_status():
    return {'status': bot_status, 'active_routines': list(active_routines)}