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
from webdriver_manager.chrome import ChromeDriverManager
from pynput import mouse, keyboard
from selenium.common.exceptions import WebDriverException, JavascriptException

logging.basicConfig(level=logging.INFO)

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
        self.viewport_width = None
        self.viewport_height = None

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

            self.viewport_width = self.driver.execute_script("return window.innerWidth")
            self.viewport_height = self.driver.execute_script("return window.innerHeight")

            logging.info(f"Starting recording for routine: {self.routine_name}")
            logging.info(f"Viewport size during recording: {self.viewport_width}x{self.viewport_height}")
            logging.info("Press 'r' to start recording, 's' to stop recording.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            self.keyboard_listener.join()

            return {
                'actions': self.actions,
                'viewport_width': self.viewport_width,
                'viewport_height': self.viewport_height
            }
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
                device_pixel_ratio = self.driver.execute_script("return window.devicePixelRatio")

                x = x / device_pixel_ratio
                y = y / device_pixel_ratio

                relative_x = x / self.viewport_width
                relative_y = y / self.viewport_height

                action = {
                    'type': action_type,
                    'time': current_time,
                    'x': relative_x,
                    'y': relative_y
                }

                self.actions.append(action)
                logging.info(f"Recorded {action_type} at ({x}, {y})")
            except WebDriverException:
                logging.error("Browser window was closed. Stopping recording.")
                self.stop_recording()

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

class Player:
    def __init__(self, routine_name):
        self.routine_name = routine_name
        self.driver = None
        self.wait = None
        self.recorded_viewport_width = None
        self.recorded_viewport_height = None
        self.start_time = None

    def start(self, recorded_data):
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("force-device-scale-factor=1")
            chrome_options.add_argument("high-dpi-support=1")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)

            self.driver.get('https://web.telegram.org/k/')

            # Wait for the page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Ensure the window is in focus and maximized
            self.driver.maximize_window()
            self.driver.execute_script("window.focus();")

            # Wait longer for the page to settle
            time.sleep(5)

            self.recorded_viewport_width = recorded_data['viewport_width']
            self.recorded_viewport_height = recorded_data['viewport_height']

            logging.info(f"Starting playback for routine: {self.routine_name}")
            logging.info(f"Recorded viewport size: {self.recorded_viewport_width}x{self.recorded_viewport_height}")
            logging.info(f"Current window size: {self.driver.get_window_size()}")

            self.start_time = time.time()
            for action in recorded_data['actions']:
                self.wait_for_action_time(action['time'])
                self.perform_action(action)

            logging.info(f"Playback completed for routine: {self.routine_name}")
            return True
        except Exception as e:
            logging.error(f"Error during playback: {str(e)}")
            return False
        finally:
            self.cleanup()

    def wait_for_action_time(self, action_time):
        current_time = time.time() - self.start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            time.sleep(wait_time)

    def perform_action(self, action):
        if action['type'] == 'click':
            self.perform_click(action)
        # Add more action types as needed

    def perform_click(self, action):
        try:
            x = action['x']
            y = action['y']
            current_viewport_width = self.driver.execute_script("return window.innerWidth")
            current_viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Calculate the ratio between recorded and current viewport sizes
            width_ratio = current_viewport_width / self.recorded_viewport_width
            height_ratio = current_viewport_height / self.recorded_viewport_height

            # Adjust coordinates based on the ratio
            adjusted_x = int(x * width_ratio)
            adjusted_y = int(y * height_ratio)

            logging.info(f"Original click coordinates: ({x}, {y})")
            logging.info(f"Adjusted click coordinates: ({adjusted_x}, {adjusted_y})")
            logging.info(f"Current viewport size: {current_viewport_width}x{current_viewport_height}")
            logging.info(f"Recorded viewport size: {self.recorded_viewport_width}x{self.recorded_viewport_height}")

            # Ensure coordinates are within viewport
            adjusted_x = max(0, min(adjusted_x, current_viewport_width - 1))
            adjusted_y = max(0, min(adjusted_y, current_viewport_height - 1))

            # Scroll into view
            self.driver.execute_script(f"window.scrollTo({adjusted_x - (current_viewport_width/2)}, {adjusted_y - (current_viewport_height/2)});")
            time.sleep(0.5)  # Wait for scroll to complete

            # Perform the click using ActionChains
            action = ActionChains(self.driver)
            action.move_by_offset(adjusted_x, adjusted_y).click().perform()
            
            logging.info(f"Click performed at ({adjusted_x}, {adjusted_y})")

            # Reset mouse position to (0,0)
            action.move_by_offset(-adjusted_x, -adjusted_y).perform()

        except Exception as e:
            logging.error(f"Error performing click: {str(e)}")

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

def start_recording(routine_name):
    recorder = Recorder(routine_name)
    return recorder.start()

def start_playback(routine_name, recorded_data):
    player = Player(routine_name)
    return player.start(recorded_data)