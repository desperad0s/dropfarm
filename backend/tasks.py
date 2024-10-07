from backend.celery_app import celery_app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a path for user data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')

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
        driver.get('https://web.telegram.org/')
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