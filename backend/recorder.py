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

            # Wait for the page to load
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            # Inject instructions into the page
            self.inject_instructions()

            logging.info(f"Starting recording for routine: {self.routine_name}")
            logging.info("Instructions displayed in the new window.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            self.keyboard_listener.join()

            return {'actions': self.actions}
        except Exception as e:
            logging.error(f"Error during recording: {str(e)}")
            return None
        finally:
            self.cleanup()

    def inject_instructions(self):
        instructions_js = """
        var instructionsDiv = document.createElement('div');
        instructionsDiv.innerHTML = '<div style="position: fixed; top: 10px; left: 10px; background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; z-index: 9999;">Press F8 to start recording, F9 to stop recording</div>';
        document.body.appendChild(instructionsDiv);
        """
        self.driver.execute_script(instructions_js)

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
        self.show_recording_indicator()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        logging.info("Recording stopped.")
        self.hide_recording_indicator()

    def show_recording_indicator(self):
        indicator_js = """
        var indicatorDiv = document.createElement('div');
        indicatorDiv.id = 'recording-indicator';
        indicatorDiv.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background-color: red; color: white; padding: 10px; border-radius: 50%; z-index: 9999;">REC</div>';
        document.body.appendChild(indicatorDiv);
        """
        self.driver.execute_script(indicator_js)

    def hide_recording_indicator(self):
        hide_js = """
        var indicator = document.getElementById('recording-indicator');
        if (indicator) indicator.remove();
        """
        self.driver.execute_script(hide_js)

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

            # Inject instructions into the page
            self.inject_instructions()

            logging.info(f"Playback window opened for routine: {self.routine_name}")
            logging.info("Instructions displayed in the new window.")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            while not self.playback_started:
                time.sleep(0.1)

            logging.info(f"Starting playback for routine: {self.routine_name}")
            self.show_playback_indicator()

            start_time = time.time()
            for action in recorded_data['actions']:
                self.wait_for_action_time(action['time'], start_time)
                self.perform_action(action)

            self.hide_playback_indicator()
            logging.info(f"Playback completed for routine: {self.routine_name}")
            return True
        except Exception as e:
            logging.error(f"Error during playback: {str(e)}")
            return False
        finally:
            self.cleanup()

    def inject_instructions(self):
        instructions_js = """
        var instructionsDiv = document.createElement('div');
        instructionsDiv.innerHTML = '<div style="position: fixed; top: 10px; left: 10px; background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; z-index: 9999;">Press F10 to start playback</div>';
        document.body.appendChild(instructionsDiv);
        """
        self.driver.execute_script(instructions_js)

    def on_press(self, key):
        if key == keyboard.Key.f10 and not self.playback_started:
            self.playback_started = True
            logging.info("Playback started.")
            return False  # Stop listening for key presses

    def show_playback_indicator(self):
        indicator_js = """
        var indicatorDiv = document.createElement('div');
        indicatorDiv.id = 'playback-indicator';
        indicatorDiv.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background-color: green; color: white; padding: 10px; border-radius: 50%; z-index: 9999;">PLAY</div>';
        document.body.appendChild(indicatorDiv);
        """
        self.driver.execute_script(indicator_js)

    def hide_playback_indicator(self):
        hide_js = """
        var indicator = document.getElementById('playback-indicator');
        if (indicator) indicator.remove();
        """
        self.driver.execute_script(hide_js)

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