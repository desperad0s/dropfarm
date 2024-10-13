import time
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .automation_config import get_chrome_driver
from pynput import keyboard

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, routine_name, actions, repeat_indefinitely=False, iteration_delay=1):
        self.routine_name = routine_name
        self.actions = actions
        self.driver = None
        self.start_time = None
        self.is_playing = False
        self.repeat_indefinitely = repeat_indefinitely
        self.stop_requested = False
        self.iteration_delay = iteration_delay
        self.keyboard_listener = None

    def start(self):
        self.driver = get_chrome_driver()
        self.driver.get('https://web.telegram.org/k/')
        logger.info(f"Started player for routine: {self.routine_name}")
        
        # Ensure the window is maximized and fullscreen
        self.driver.maximize_window()
        self.driver.fullscreen_window()
        
        self.setup_ui()
        self.setup_global_listeners()
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
        statusDiv.innerHTML = 'Press 7 to start playback. Press 8 to stop playback.';
        document.body.appendChild(statusDiv);
        """
        self.driver.execute_script(js_code)

    def setup_global_listeners(self):
        def on_press(key):
            try:
                if key.char == '7' and not self.is_playing:
                    self.driver.execute_script("window.playbackStarted = true;")
                elif key.char == '8' and self.is_playing:
                    self.driver.execute_script("window.playbackStopped = true;")
            except AttributeError:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def wait_for_start_signal(self):
        logger.info("Waiting for '7' key press to start playback...")
        self.driver.execute_script("""
        window.playbackStarted = false;
        window.playbackStopped = false;
        """)
        
        try:
            WebDriverWait(self.driver, 600).until(
                lambda d: d.execute_script("return window.playbackStarted === true || window.playbackStopped === true;")
            )
        except TimeoutException:
            logger.info("Playback start/stop timed out after 10 minutes.")
            return
        
        if self.driver.execute_script("return window.playbackStopped === true;"):
            logger.info("Stop signal received before playback started. Closing session.")
            self.stop_requested = True
            return

        logger.info("Playback start signal received.")
        self.start_time = time.time()
        self.is_playing = True
        self.play()

    def play(self):
        if self.repeat_indefinitely:
            self.play_indefinitely()
        else:
            self.play_once()

    def play_once(self):
        if not self.actions['actions']:
            logger.warning("No actions to play")
            return

        self.start_time = time.time()
        for action in self.actions['actions']:
            if self.check_for_stop_signal():
                break
            self.wait_for_action_time(action['time'])
            if action['type'] == 'click':
                self.perform_click(action['x'], action['y'])

        logger.info("Single playback completed")
        self.driver.execute_script("document.getElementById('playback-status').innerHTML = 'Playback completed';")
        self.is_playing = False

    def play_indefinitely(self):
        if not self.actions['actions']:
            logger.warning("No actions to play")
            return

        while not self.stop_requested:
            self.start_time = time.time()
            for action in self.actions['actions']:
                if self.check_for_stop_signal():
                    break
                self.wait_for_action_time(action['time'])
                if action['type'] == 'click':
                    self.perform_click(action['x'], action['y'])
            
            if self.stop_requested:
                break
            
            logger.info(f"Routine iteration completed, waiting for {self.iteration_delay} seconds before restarting...")
            self.driver.execute_script(f"document.getElementById('playback-status').innerHTML = 'Routine completed, restarting in {self.iteration_delay} seconds... Press 8 to stop.';")
            
            # Wait for the delay, checking for stop signal every second
            for _ in range(int(self.iteration_delay)):
                time.sleep(1)
                if self.check_for_stop_signal():
                    break

        logger.info("Indefinite playback stopped")
        self.driver.execute_script("document.getElementById('playback-status').innerHTML = 'Playback stopped';")
        self.is_playing = False

    def check_for_stop_signal(self):
        if self.driver.execute_script("return window.playbackStopped === true;"):
            logger.info("Stop signal received. Stopping playback.")
            self.stop_requested = True
            self.is_playing = False
            return True
        return False

    def wait_for_action_time(self, action_time):
        current_time = time.time() - self.start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            logger.debug(f"Waiting for {wait_time:.2f} seconds before next action")
            end_time = time.time() + wait_time
            while time.time() < end_time:
                if self.check_for_stop_signal():
                    return
                time.sleep(0.1)

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
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.driver:
            self.driver.quit()
        logger.info(f"Stopped playback for routine: {self.routine_name}")

def start_playback(routine_name, actions, repeat_indefinitely=False, iteration_delay=1):
    logger.info(f"Starting {'repeat' if repeat_indefinitely else 'solo'} playback for routine: {routine_name}")
    logger.info(f"Number of actions: {len(actions['actions'])}")
    logger.info(f"Repeat: {repeat_indefinitely}, Iteration delay: {iteration_delay} seconds")
    player = Player(routine_name, actions, repeat_indefinitely, iteration_delay)
    player.start()
    return player
