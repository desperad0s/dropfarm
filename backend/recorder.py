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

logging.basicConfig(level=logging.INFO)

CHROME_USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'chrome_user_data', 'Default')

class Recorder:
    def __init__(self, routine_name):
        self.routine_name = routine_name
        self.recording = False
        self.actions = []
        self.start_time = None
        self.driver = None
        self.mouse_listener = None
        self.keyboard_listener = None

    def start(self):
        try:
            os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)

            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.get('https://web.telegram.org/k/')

            logging.info(f"Starting recording for routine: {self.routine_name}")
            logging.info("Press 'F8' to start recording, 'F9' to stop recording.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            self.keyboard_listener.join()

            return {'actions': self.actions}
        except Exception as e:
            logging.error(f"Error during recording: {str(e)}")
            return None
        finally:
            self.cleanup()

    def on_press(self, key):
        if key == keyboard.Key.f8 and not self.recording:
            self.start_recording()
        elif key == keyboard.Key.f9 and self.recording:
            self.stop_recording()
            return False

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        logging.info("Recording started. Press 'F9' to stop recording.")
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        logging.info("Recording stopped.")

    def on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            current_time = time.time() - self.start_time
            action = {
                'type': 'click',
                'time': current_time,
                'x': x,
                'y': y
            }
            self.actions.append(action)
            logging.info(f"Recorded click at ({x}, {y})")

    def cleanup(self):
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            self.driver.quit()

class Player:
    def __init__(self, routine_name):
        self.routine_name = routine_name
        self.driver = None
        self.keyboard_listener = None
        self.playback_started = False

    def start(self, recorded_data):
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.get('https://web.telegram.org/k/')

            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            logging.info(f"Playback window opened for routine: {self.routine_name}")
            logging.info("Press 'F10' to start playback.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            while not self.playback_started:
                time.sleep(0.1)

            logging.info(f"Starting playback for routine: {self.routine_name}")

            start_time = time.time()
            for action in recorded_data['actions']:
                self.wait_for_action_time(action['time'], start_time)
                self.perform_action(action)

            logging.info(f"Playback completed for routine: {self.routine_name}")
            return True
        except Exception as e:
            logging.error(f"Error during playback: {str(e)}")
            return False
        finally:
            self.cleanup()

    def on_press(self, key):
        if key == keyboard.Key.f10 and not self.playback_started:
            self.playback_started = True
            logging.info("Playback started.")
            return False  # Stop listening for key presses

    def wait_for_action_time(self, action_time, start_time):
        current_time = time.time() - start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            time.sleep(wait_time)

    def perform_action(self, action):
        if action['type'] == 'click':
            self.perform_click(action)

    def perform_click(self, action):
        try:
            x, y = action['x'], action['y']
            action_chains = ActionChains(self.driver)
            action_chains.move_by_offset(x, y).click().perform()
            action_chains.move_by_offset(-x, -y).perform()  # Reset mouse position
            logging.info(f"Click performed at ({x}, {y})")
        except Exception as e:
            logging.error(f"Error performing click: {str(e)}")

    def cleanup(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            self.driver.quit()

def start_recording(routine_name):
    recorder = Recorder(routine_name)
    return recorder.start()

def start_playback(routine_name, recorded_data):
    player = Player(routine_name)
    return player.start(recorded_data)