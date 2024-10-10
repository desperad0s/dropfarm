import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from pynput import mouse, keyboard
from selenium.common.exceptions import WebDriverException

logging.basicConfig(level=logging.INFO)

# Use a single, consistent user data directory for all sessions
CHROME_USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'chrome_user_data', 'Default')

class Recorder:
    def __init__(self, routine_name):
        self.routine_name = routine_name
        self.recording = False
        self.actions = []
        self.start_time = None
        self.driver = None
        self.wait = None
        self.mouse_listener = None
        self.keyboard_listener = None

    def start(self):
        try:
            os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)

            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("force-device-scale-factor=1")
            chrome_options.add_argument("high-dpi-support=1")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            self.driver.execute_script("document.body.style.zoom='100%'")
            self.driver.get('https://web.telegram.org/k/')

            logging.info(f"Starting recording for routine: {self.routine_name}")
            logging.info("Press 'r' to start recording, 's' to stop recording.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            self.keyboard_listener.join()

            return self.actions
        except Exception as e:
            logging.error(f"Error during recording: {str(e)}")
            return None
        finally:
            self.cleanup()

    def on_press(self, key):
        try:
            if key.char == 'r' and not self.recording:
                self.start_recording()
            elif key.char == 's' and self.recording:
                self.stop_recording()
                return False
        except AttributeError:
            pass

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        logging.info("Recording started. Press 's' to stop recording.")
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        logging.info("Recording stopped.")

    def on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            try:
                self.record_action('click', x, y)
            except WebDriverException:
                logging.error("Browser window was closed. Stopping recording.")
                self.stop_recording()

    def record_action(self, action_type, x, y):
        if self.recording:
            try:
                current_time = time.time() - self.start_time
                viewport_width = self.driver.execute_script("return window.innerWidth")
                viewport_height = self.driver.execute_script("return window.innerHeight")
                device_pixel_ratio = self.driver.execute_script("return window.devicePixelRatio")

                x = x / device_pixel_ratio
                y = y / device_pixel_ratio

                relative_x = x / viewport_width
                relative_y = y / viewport_height

                element = self.driver.execute_script(
                    "return document.elementFromPoint(arguments[0], arguments[1]);",
                    x, y
                )

                action = {
                    'type': action_type,
                    'time': current_time,
                    'x': relative_x,
                    'y': relative_y,
                    'xpath': self.get_xpath(element) if element else None,
                    'tag_name': element.tag_name if element else None,
                    'text': element.text if element else None
                }

                self.actions.append(action)
                logging.info(f"Recorded {action_type} at ({x}, {y})")
            except WebDriverException:
                logging.error("Browser window was closed. Stopping recording.")
                self.stop_recording()

    def get_xpath(self, element):
        components = []
        child = element
        while child:
            parent = child.find_element(By.XPATH, '..')
            children = parent.find_elements(By.XPATH, '*')
            index = children.index(child) + 1
            tag_name = child.tag_name
            components.insert(0, f'{tag_name}[{index}]')
            child = parent
            if child.tag_name == 'html':
                break
        return '/' + '/'.join(components)

    def cleanup(self):
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

def start_recording(routine_name):
    recorder = Recorder(routine_name)
    return recorder.start()