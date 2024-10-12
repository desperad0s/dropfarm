import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, routine_name, actions):
        self.routine_name = routine_name
        self.actions = actions
        self.driver = None
        self.start_time = None

    def start(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('https://web.telegram.org/k/')
        self.driver.fullscreen_window()
        logger.info(f"Started player for routine: {self.routine_name}")
        
        self.setup_ui()
        self.setup_start_trigger()
        self.wait_for_start_signal()

    def setup_ui(self):
        js_code = """
        var statusDiv = document.createElement('div');
        statusDiv.id = 'playback-status';
        statusDiv.style.position = 'fixed';
        statusDiv.style.top = '10px';
        statusDiv.style.left = '10px';
        statusDiv.style.padding = '10px';
        statusDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        statusDiv.style.color = 'white';
        statusDiv.style.zIndex = '9999999';
        statusDiv.innerHTML = 'Press 9 to start playback';
        document.body.appendChild(statusDiv);
        """
        self.driver.execute_script(js_code)

    def setup_start_trigger(self):
        js_code = """
        document.addEventListener('keydown', function(e) {
            if (e.key === '9') {
                window.dispatchEvent(new CustomEvent('startPlayback'));
                document.getElementById('playback-status').innerHTML = 'Playback started';
            }
        });
        """
        self.driver.execute_script(js_code)

    def wait_for_start_signal(self):
        logger.info("Waiting for '9' key press to start playback...")
        self.driver.execute_script("""
        window.playbackStarted = false;
        window.addEventListener('startPlayback', function() {
            window.playbackStarted = true;
        });
        """)
        
        WebDriverWait(self.driver, 600).until(
            lambda d: d.execute_script("return window.playbackStarted === true;")
        )
        logger.info("Playback start signal received.")
        self.start_time = time.time()

    def play(self):
        if not self.actions['actions']:
            logger.warning("No actions to play")
            return

        for action in self.actions['actions']:
            self.wait_for_action_time(action['time'])
            if action['type'] == 'click':
                self.perform_click(action['x'], action['y'])

        logger.info("Playback completed")
        self.driver.execute_script("document.getElementById('playback-status').innerHTML = 'Playback completed';")

    def wait_for_action_time(self, action_time):
        current_time = time.time() - self.start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            logger.debug(f"Waiting for {wait_time:.2f} seconds before next action")
            time.sleep(wait_time)

    def perform_click(self, x, y):
        self.show_click_indicator(x, y)
        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y).click().perform()
        actions.move_by_offset(-x, -y).perform()  # Reset mouse position
        logger.debug(f"Performed click at ({x}, {y})")

    def show_click_indicator(self, x, y):
        js_code = """
        var clickIndicator = document.createElement('div');
        clickIndicator.style.position = 'fixed';
        clickIndicator.style.left = arguments[0] + 'px';
        clickIndicator.style.top = arguments[1] + 'px';
        clickIndicator.style.width = '10px';
        clickIndicator.style.height = '10px';
        clickIndicator.style.borderRadius = '50%';
        clickIndicator.style.backgroundColor = 'rgba(0, 255, 0, 0.5)';
        clickIndicator.style.zIndex = '9999';
        document.body.appendChild(clickIndicator);
        setTimeout(function() {
            clickIndicator.remove();
        }, 2000);
        """
        self.driver.execute_script(js_code, x, y)

    def stop(self):
        if self.driver:
            self.driver.quit()
        logger.info(f"Stopped playback for routine: {self.routine_name}")

def start_playback(routine_name, actions):
    player = Player(routine_name, actions)
    player.start()
    player.play()
    player.stop()
    return True
