import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, routine_name, actions, repeat=False):
        self.routine_name = routine_name
        self.actions = actions
        self.driver = None
        self.start_time = None
        self.is_playing = False
        self.repeat = repeat
        self.stop_requested = False
        self.session_active = True
        self.chrome_options = self.setup_chrome_options()

    def setup_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Use the root chrome_user_data directory
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        
        return chrome_options

    def start(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
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
        statusDiv.innerHTML = 'Press 9 to start playback<br>Press 0 to stop and close';
        document.body.appendChild(statusDiv);

        var playingIndicator = document.createElement('div');
        playingIndicator.id = 'playing-indicator';
        playingIndicator.style.position = 'fixed';
        playingIndicator.style.top = '10px';
        playingIndicator.style.right = '10px';
        playingIndicator.style.padding = '10px';
        playingIndicator.style.backgroundColor = 'green';
        playingIndicator.style.color = 'white';
        playingIndicator.style.zIndex = '9999999';
        playingIndicator.style.display = 'none';
        playingIndicator.innerHTML = 'Playing';
        document.body.appendChild(playingIndicator);
        """
        self.driver.execute_script(js_code)

    def setup_start_trigger(self):
        js_code = """
        document.addEventListener('keydown', function(e) {
            if (e.key === '9') {
                window.dispatchEvent(new CustomEvent('startPlayback'));
            } else if (e.key === '0') {
                window.dispatchEvent(new CustomEvent('stopPlayback'));
            }
        });
        """
        self.driver.execute_script(js_code)

    def wait_for_start_signal(self):
        logger.info("Waiting for '9' key press to start/resume playback...")
        self.driver.execute_script("""
        window.playbackStarted = false;
        window.addEventListener('startPlayback', function() {
            window.playbackStarted = true;
        });
        window.addEventListener('stopPlayback', function() {
            window.playbackStopped = true;
        });
        """)
        
        try:
            WebDriverWait(self.driver, 600).until(
                lambda d: d.execute_script("return window.playbackStarted === true || window.playbackStopped === true;")
            )
        except TimeoutException:
            logger.info("Playback start/stop timed out after 10 minutes.")
            self.session_active = False
            return
        
        if self.driver.execute_script("return window.playbackStopped === true;"):
            logger.info("Stop signal received. Closing session.")
            self.session_active = False
            return

        logger.info("Playback start signal received.")
        self.start_time = time.time()
        self.is_playing = True
        self.stop_requested = False
        self.driver.execute_script("document.getElementById('playing-indicator').style.display = 'block';")

    def play(self):
        if not self.actions['actions']:
            logger.warning("No actions to play")
            return

        while self.session_active:
            if self.is_playing:
                for action in self.actions['actions']:
                    if self.stop_requested:
                        break
                    self.wait_for_action_time(action['time'])
                    if action['type'] == 'click':
                        self.perform_click(action['x'], action['y'])
                
                if not self.repeat:
                    self.is_playing = False
                    logger.info("Solo playback completed, waiting for user input")
                    self.driver.execute_script("""
                    document.getElementById('playback-status').innerHTML = 'Solo playback completed<br>Press 9 to replay<br>Press 0 to close';
                    document.getElementById('playing-indicator').style.display = 'none';
                    """)
                else:
                    self.start_time = time.time()  # Reset start time for next iteration
            else:
                # Wait for user input to start playing again or stop
                self.wait_for_start_signal()
                if not self.session_active:
                    break

        logger.info("Playback session ended")
        self.driver.execute_script("""
        document.getElementById('playback-status').innerHTML = 'Playback session ended';
        document.getElementById('playing-indicator').style.display = 'none';
        """)
        self.driver.quit()

    def wait_for_action_time(self, action_time):
        current_time = time.time() - self.start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            logger.debug(f"Waiting for {wait_time:.2f} seconds before next action")
            time.sleep(wait_time)

    def perform_click(self, x, y):
        window_size = self.driver.get_window_size()
        actual_x = int(x * window_size['width'])
        actual_y = int(y * window_size['height'])
        logger.info(f"Clicking at relative position ({x}, {y}), actual position ({actual_x}, {actual_y})")
        self.show_click_indicator(actual_x, actual_y)
        actions = ActionChains(self.driver)
        actions.move_by_offset(actual_x, actual_y).click().perform()
        actions.move_by_offset(-actual_x, -actual_y).perform()  # Reset mouse position

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
        self.stop_requested = True
        self.is_playing = False
        self.session_active = False
        if self.driver:
            self.driver.quit()
        logger.info(f"Stopped playback for routine: {self.routine_name}")

def start_playback(routine_name, actions, repeat=False):
    logger.info(f"Starting {'repeat' if repeat else 'solo'} playback for routine: {routine_name}")
    logger.info(f"Number of actions: {len(actions['actions'])}")
    logger.info(f"Repeat: {repeat}")
    player = Player(routine_name, actions, repeat)
    player.start()
    return player
