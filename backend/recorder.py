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
from .calibration import Calibrator

logging.basicConfig(level=logging.INFO)

CHROME_USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'chrome_user_data', 'Default')
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720  # 16:9 aspect ratio

class Recorder:
    def __init__(self, routine_name, calibration_data=None):
        self.routine_name = routine_name
        self.recording = False
        self.actions = []
        self.start_time = None
        self.driver = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.viewport_size = None
        self.offset = None
        self.calibrator = Calibrator(calibration_data) if calibration_data else None

    def start(self):
        try:
            os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)

            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument(f"window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Use ChromeDriverManager to get the latest compatible ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.driver.set_window_position(0, 0)
            self.driver.get('https://web.telegram.org/k/')

            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            self.driver.execute_script("document.body.style.zoom='100%'")

            self.viewport_size = self.get_viewport_size()
            self.offset = self.calculate_offset()
            logging.info(f"Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            logging.info(f"Viewport size: {self.viewport_size['width']}x{self.viewport_size['height']}")
            logging.info(f"Calculated offset: {self.offset}")
            logging.info(f"Viewport size: {self.viewport_size}")
            logging.info(f"Viewport offset: {self.offset}")

            self.inject_instructions()

            logging.info(f"Starting recording for routine: {self.routine_name}")

            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()

            # Wait for user to start recording
            while not self.recording:
                time.sleep(0.1)

            # Record until user stops
            while self.recording:
                time.sleep(0.1)

            return {'actions': self.actions, 'viewport_size': self.viewport_size}
        except Exception as e:
            logging.error(f"Error during recording: {str(e)}")
            return None
        finally:
            self.cleanup()

    def get_viewport_size(self):
        return self.driver.execute_script("""
            return {
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
            }
        """)

    def calculate_offset(self):
        return self.driver.execute_script("""
            var body = document.body;
            var html = document.documentElement;
            var windowHeight = window.innerHeight;
            var documentHeight = Math.max(
                body.scrollHeight, body.offsetHeight,
                html.clientHeight, html.scrollHeight, html.offsetHeight
            );
            return {
                x: window.pageXOffset,
                y: window.pageYOffset + (documentHeight > windowHeight ? windowHeight - documentHeight : 0)
            };
        """)

    def inject_instructions(self):
        instructions_js = """
        function injectInstructions() {
            var instructionsDiv = document.createElement('div');
            instructionsDiv.innerHTML = '<div style="position: fixed; top: 10px; left: 10px; background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; z-index: 9999; pointer-events: none;">Press 7 to start recording, 8 to stop recording</div>';
            document.body.appendChild(instructionsDiv);
        }
        setTimeout(injectInstructions, 2000);  // Delay injection by 2 seconds
        """
        self.driver.execute_script(instructions_js)

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('7') and not self.recording:
            self.start_recording()
        elif key == keyboard.KeyCode.from_char('8') and self.recording:
            self.stop_recording()
            return False

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        logging.info("Recording started. Press '8' to stop recording.")
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
        function showRecordingIndicator() {
            var indicatorDiv = document.createElement('div');
            indicatorDiv.id = 'recording-indicator';
            indicatorDiv.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background-color: rgba(255, 0, 0, 0.7); color: white; padding: 10px; border-radius: 50%; z-index: 9999; pointer-events: none; display: flex; align-items: center; justify-content: center; width: 50px; height: 50px; font-size: 12px; font-weight: bold;">REC</div>';
            document.body.appendChild(indicatorDiv);
        }
        setTimeout(showRecordingIndicator, 100);  // Small delay to ensure it's added after any page updates
        """
        self.driver.execute_script(indicator_js)

    def hide_recording_indicator(self):
        hide_js = """
        var indicator = document.getElementById('recording-indicator');
        if (indicator) indicator.remove();
        """
        try:
            if self.driver:
                self.driver.execute_script(hide_js)
        except Exception as e:
            logging.error(f"Error hiding recording indicator: {str(e)}")

    def on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            current_time = time.time() - self.start_time
            try:
                if self.calibrator and self.calibrator.is_calibrated():
                    transformed_x, transformed_y = self.calibrator.transform_coordinate(x, y)
                else:
                    transformed_x, transformed_y = x, y
                action = {
                    'type': 'click',
                    'time': current_time,
                    'x': transformed_x,
                    'y': transformed_y
                }
                self.actions.append(action)
                logging.info(f"Raw click at ({x}, {y})")
                logging.info(f"Transformed click at ({transformed_x}, {transformed_y})")
            except Exception as e:
                logging.error(f"Error during click recording: {str(e)}")
                # Use original coordinates if transformation fails
                action = {
                    'type': 'click',
                    'time': current_time,
                    'x': x,
                    'y': y
                }
                self.actions.append(action)
                logging.info(f"Recorded click at original coordinates ({x}, {y}) due to error")

    def cleanup(self):
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            self.driver.quit()

class Player:
    def __init__(self, routine_name, calibration_data=None):
        self.routine_name = routine_name
        self.driver = None
        self.keyboard_listener = None
        self.playback_started = False
        self.viewport_size = None
        self.offset = None
        self.calibrator = Calibrator(calibration_data)
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def start(self, recorded_data):
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
            chrome_options.add_argument(f"window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Use ChromeDriverManager to get the latest compatible ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.driver.set_window_position(0, 0)
            self.driver.get('https://web.telegram.org/k/')

            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            self.driver.execute_script("document.body.style.zoom='100%'")

            self.viewport_size = self.get_viewport_size()
            self.offset = self.calculate_offset()
            logging.info(f"Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            logging.info(f"Viewport size: {self.viewport_size['width']}x{self.viewport_size['height']}")
            logging.info(f"Calculated offset: {self.offset}")
            logging.info(f"Viewport size: {self.viewport_size}")
            logging.info(f"Viewport offset: {self.offset}")

            self.inject_instructions()

            logging.info(f"Playback window opened for routine: {self.routine_name}")

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

    def get_viewport_size(self):
        return self.driver.execute_script("""
            return {
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
            }
        """)

    def calculate_offset(self):
        return self.driver.execute_script("""
            var body = document.body;
            var html = document.documentElement;
            var windowHeight = window.innerHeight;
            var documentHeight = Math.max(
                body.scrollHeight, body.offsetHeight,
                html.clientHeight, html.scrollHeight, html.offsetHeight
            );
            return {
                x: window.pageXOffset,
                y: window.pageYOffset + (documentHeight > windowHeight ? windowHeight - documentHeight : 0)
            };
        """)

    def inject_instructions(self):
        instructions_js = """
        function injectInstructions() {
            var instructionsDiv = document.createElement('div');
            instructionsDiv.innerHTML = '<div style="position: fixed; top: 10px; left: 10px; background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; z-index: 9999; pointer-events: none;">Press 9 to start playback</div>';
            document.body.appendChild(instructionsDiv);
        }
        setTimeout(injectInstructions, 2000);  // Delay injection by 2 seconds
        """
        self.driver.execute_script(instructions_js)

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('9') and not self.playback_started:
            self.playback_started = True
            logging.info("Playback started.")
            return False  # Stop listening for key presses

    def show_playback_indicator(self):
        indicator_js = """
        function showPlaybackIndicator() {
            var indicatorDiv = document.createElement('div');
            indicatorDiv.id = 'playback-indicator';
            indicatorDiv.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background-color: rgba(0, 255, 0, 0.7); color: white; padding: 10px; border-radius: 50%; z-index: 9999; pointer-events: none; display: flex; align-items: center; justify-content: center; width: 50px; height: 50px; font-size: 12px; font-weight: bold;">PLAY</div>';
            document.body.appendChild(indicatorDiv);
        }
        setTimeout(showPlaybackIndicator, 100);  // Small delay to ensure it's added after any page updates
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

    def show_click_indicator(self, x, y):
        js_code = """
        var clickIndicator = document.createElement('div');
        clickIndicator.style.position = 'absolute';
        clickIndicator.style.left = arguments[0] + 'px';
        clickIndicator.style.top = arguments[1] + 'px';
        clickIndicator.style.width = '20px';
        clickIndicator.style.height = '20px';
        clickIndicator.style.borderRadius = '50%';
        clickIndicator.style.border = '2px solid red';
        clickIndicator.style.zIndex = '9999';
        clickIndicator.style.pointerEvents = 'none';
        document.body.appendChild(clickIndicator);
        setTimeout(function() {
            clickIndicator.remove();
        }, 1000);
        """
        self.driver.execute_script(js_code, x, y)

    def perform_click(self, action):
        try:
            if self.calibrator and self.calibrator.is_calibrated():
                x, y = self.calibrator.transform_coordinate(action['x'], action['y'])
            else:
                x, y = action['x'], action['y']
            
            # Show click indicator before performing the click
            self.show_click_indicator(x, y)
            
            # Take a screenshot
            screenshot_path = os.path.join(self.screenshot_dir, f"click_indicator_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved: {screenshot_path}")
            
            action_chains = ActionChains(self.driver)
            action_chains.move_by_offset(x, y).click().perform()
            action_chains.move_by_offset(-x, -y).perform()  # Reset mouse position
            logging.info(f"Click performed at ({x}, {y})")
            
            # Add a small delay to allow the indicator to be visible
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Error performing click: {str(e)}")

    def cleanup(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            self.driver.quit()

def start_recording(routine_name, calibration_data=None):
    try:
        recorder = Recorder(routine_name, calibration_data)
        return recorder.start()
    except Exception as e:
        logging.error(f"Error in start_recording: {str(e)}")
        return None

def start_playback(routine_name, recorded_data, calibration_data=None):
    player = Player(routine_name, calibration_data)
    return player.start(recorded_data)