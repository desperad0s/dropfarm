from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')
RECORDED_ROUTINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_routines')
os.makedirs(RECORDED_ROUTINES_DIR, exist_ok=True)

class RecordingListener(AbstractEventListener):
    def __init__(self):
        self.actions = []
        self.last_action_time = time.time()
        self.last_mouse_position = None
        self.mouse_move_threshold = 50  # Increased threshold to reduce number of recorded movements

    def before_click(self, element, driver):
        action = {
            'type': 'click',
            'selector': self.get_css_selector(element, driver),
            'x': element.location['x'],
            'y': element.location['y'],
            'timestamp': time.time()
        }
        self.actions.append(action)
        logger.debug(f"Recorded click: {action}")

    def before_change_value_of(self, element, driver):
        action = {
            'type': 'input',
            'selector': self.get_css_selector(element, driver),
            'value': element.get_attribute('value'),
            'timestamp': time.time()
        }
        self.actions.append(action)
        logger.debug(f"Recorded input: {action}")

    def before_navigate_to(self, url, driver):
        action = {
            'type': 'navigate',
            'url': url,
            'timestamp': time.time()
        }
        self.actions.append(action)
        logger.debug(f"Recorded navigation: {action}")

    def get_css_selector(self, element, driver):
        return driver.execute_script("""
            function cssPath(el) {
                if (!(el instanceof Element)) return;
                var path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    var selector = el.nodeName.toLowerCase();
                    if (el.id) {
                        selector += '#' + el.id;
                        path.unshift(selector);
                        break;
                    } else {
                        var sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() == selector)
                               nth++;
                        }
                        if (nth != 1)
                            selector += ":nth-of-type("+nth+")";
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            }
            return cssPath(arguments[0]);
        """, element)

class Recorder:
    def __init__(self):
        self.driver = None
        self.listener = RecordingListener()
        self.is_recording = False
        self.start_time = None
        self.last_action_time = None
        self.last_position = None
        self.window_width = None
        self.window_height = None

    def start_recording(self, url='https://web.telegram.org/k/'):
        if self.is_recording:
            return "Recording is already in progress."
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-data-dir={USER_DATA_DIR}')
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver = EventFiringWebDriver(driver, self.listener)
        self.driver.get(url)
        self.is_recording = True
        self.start_time = time.time()
        
        # Get window size
        window_size = self.driver.get_window_size()
        self.window_width = window_size['width']
        self.window_height = window_size['height']
        
        # Inject JavaScript to track mouse movements and clicks
        self.driver.execute_script("""
            window.recordedActions = [];
            document.addEventListener('mousemove', function(e) {
                window.recordedActions.push({
                    type: 'mousemove',
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                });
            });
            document.addEventListener('click', function(e) {
                window.recordedActions.push({
                    type: 'click',
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                });
            });
        """)
        
        # Add a visible indicator that recording is in progress
        self.driver.execute_script("""
            var indicator = document.createElement('div');
            indicator.textContent = 'Recording in progress';
            indicator.style.position = 'fixed';
            indicator.style.top = '10px';
            indicator.style.right = '10px';
            indicator.style.backgroundColor = 'red';
            indicator.style.color = 'white';
            indicator.style.padding = '5px';
            indicator.style.zIndex = '9999';
            document.body.appendChild(indicator);
        """)
        
        logger.info("Recording started")
        return "Recording started. Perform your actions in the browser. A red indicator will show that recording is in progress."

    def stop_recording(self, routine_name):
        if not self.is_recording:
            return "No recording in progress."
        
        # Retrieve recorded actions
        recorded_actions = self.driver.execute_script("return window.recordedActions;")
        
        self.driver.quit()
        self.is_recording = False
        
        total_duration = time.time() - self.start_time
        
        # Combine Selenium actions with recorded actions
        all_actions = self.listener.actions + recorded_actions
        all_actions.sort(key=lambda x: x['timestamp'])
        
        processed_actions = []
        last_action_time = self.start_time
        last_mouse_position = None
        
        for action in all_actions:
            current_time = action['timestamp'] / 1000 if isinstance(action['timestamp'], int) else action['timestamp']
            
            # Add wait action if necessary
            wait_time = current_time - last_action_time
            if wait_time > 0.5:
                processed_actions.append({
                    'type': 'wait',
                    'duration': round(wait_time, 2)
                })
            
            # Process the action
            if action['type'] == 'mousemove':
                if last_mouse_position is None or \
                   abs(action['x'] - last_mouse_position[0]) > self.listener.mouse_move_threshold or \
                   abs(action['y'] - last_mouse_position[1]) > self.listener.mouse_move_threshold:
                    processed_actions.append(action)
                    last_mouse_position = (action['x'], action['y'])
            else:
                processed_actions.append(action)
                if action['type'] == 'click':
                    last_mouse_position = (action['x'], action['y'])
            
            last_action_time = current_time
        
        file_path = os.path.join(RECORDED_ROUTINES_DIR, f'{routine_name}_actions.json')
        with open(file_path, 'w') as f:
            json.dump({
                'total_duration': round(total_duration, 2),
                'window_width': self.window_width,
                'window_height': self.window_height,
                'actions': processed_actions
            }, f, indent=2)
        
        logger.info(f"Recording stopped. Actions saved to {file_path}. Total duration: {round(total_duration, 2)} seconds")
        return f"Recording stopped. Actions saved to {file_path}. Total duration: {round(total_duration, 2)} seconds"

recorder = Recorder()

if __name__ == "__main__":
    recorder.start_recording()
    input("Press Enter to stop recording...")
    recorder.stop_recording("test_routine")