import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    
    # Optimize for automation
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Set user data directory
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    
    return chrome_options

def setup_chrome_driver():
    chrome_options = get_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_chrome_driver():
    driver = setup_chrome_driver()
    
    # Maximize and fullscreen the window
    driver.maximize_window()
    driver.fullscreen_window()
    
    # Wait for the browser to be in fullscreen mode
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return window.outerWidth == screen.width && window.outerHeight == screen.height")
    )
    
    return driver
