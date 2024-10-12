import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pynput import mouse, keyboard
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Recorder:
    def __init__(self, routine_name):
        self.routine_name = routine_name
        self.actions = []
        self.start_time = None
        self.driver = None
        self.is_recording = False
        self.mouse_listener = None
        self.keyboard_listener = None
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
        logger.info(f"Started recorder for routine: {self.routine_name}")
        
        self.setup_listeners()
        self.setup_ui()
        
        try:
            WebDriverWait(self.driver, 600).until(
                EC.presence_of_element_located((By.ID, "recording-complete"))
            )
        except TimeoutException:
            logger.info("Recording timed out after 10 minutes.")
        finally:
            self.stop_recording()

    def setup_listeners(self):
        def on_click(x, y, button, pressed):
            if pressed and self.is_recording:
                current_time = time.time() - self.start_time
                self.actions.append({
                    'type': 'click',
                    'time': current_time,
                    'x': x,
                    'y': y
                })
                logger.debug(f"Recorded click at ({x}, {y}) at time {current_time:.2f}s")
                self.show_click_indicator(x, y)

        def on_press(key):
            try:
                if key.char == '7' and not self.is_recording:
                    self.start_recording()
                elif key.char == '8' and self.is_recording:
                    self.stop_recording()
            except AttributeError:
                pass

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def setup_ui(self):
        js_code = """
        var statusDiv = document.createElement('div');
        statusDiv.id = 'recording-status';
        statusDiv.style.position = 'fixed';
        statusDiv.style.top = '10px';
        statusDiv.style.left = '10px';
        statusDiv.style.padding = '10px';
        statusDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        statusDiv.style.color = 'white';
        statusDiv.style.zIndex = '9999999';
        statusDiv.innerHTML = 'Press 7 to start recording, 8 to stop';
        document.body.appendChild(statusDiv);
        """
        self.driver.execute_script(js_code)

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        logger.info("Recording started")
        self.driver.execute_script("document.getElementById('recording-status').innerHTML = 'Recording... Press 8 to stop';")

    def stop_recording(self):
        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.driver.execute_script("""
            document.getElementById('recording-status').innerHTML = 'Recording stopped';
            var completionSignal = document.createElement('div');
            completionSignal.id = 'recording-complete';
            document.body.appendChild(completionSignal);
        """)

    def show_click_indicator(self, x, y):
        js_code = """
        var clickIndicator = document.createElement('div');
        clickIndicator.style.position = 'fixed';
        clickIndicator.style.left = arguments[0] + 'px';
        clickIndicator.style.top = arguments[1] + 'px';
        clickIndicator.style.width = '10px';
        clickIndicator.style.height = '10px';
        clickIndicator.style.borderRadius = '50%';
        clickIndicator.style.backgroundColor = 'rgba(255, 0, 0, 0.5)';
        clickIndicator.style.zIndex = '9999999';
        clickIndicator.style.pointerEvents = 'none';
        document.body.appendChild(clickIndicator);
        setTimeout(function() {
            clickIndicator.remove();
        }, 2000);
        """
        try:
            self.driver.execute_script(js_code, x, y)
        except Exception as e:
            logger.error(f"Failed to show click indicator: {str(e)}")

    def stop(self):
        if self.driver:
            self.driver.quit()
        logger.info(f"Stopped recording for routine: {self.routine_name}")
        return {'actions': self.actions}

def start_recording(routine_name):
    recorder = Recorder(routine_name)
    recorder.start()
    return recorder.stop()
