from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

# Define a path for user data
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_user_data')

class Recorder:
    def __init__(self):
        self.driver = None
        self.actions = []
        self.is_recording = False

    def start_recording(self, url='https://web.telegram.org/k/'):  # Updated URL
        if self.is_recording:
            return "Recording is already in progress."
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-data-dir={USER_DATA_DIR}')
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(url)
        self.is_recording = True
        self.actions = []
        
        # Set up event listeners
        self.driver.execute_script("""
            window.recordedActions = [];
            document.addEventListener('click', function(e) {
                window.recordedActions.push({
                    type: 'click',
                    selector: cssPath(e.target),
                    x: e.clientX,
                    y: e.clientY
                });
                console.log('Click recorded');
            });
            document.addEventListener('input', function(e) {
                window.recordedActions.push({
                    type: 'input',
                    selector: cssPath(e.target),
                    value: e.target.value
                });
                console.log('Input recorded');
            });
            document.addEventListener('mousemove', function(e) {
                window.recordedActions.push({
                    type: 'mousemove',
                    x: e.clientX,
                    y: e.clientY
                });
                console.log('Mouse move recorded');
            });
            
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
        
        return "Recording started. Perform your actions in the browser. A red indicator will show that recording is in progress."

    def stop_recording(self, routine_name):
        if not self.is_recording:
            return "No recording in progress."
        
        self.actions = self.driver.execute_script("return window.recordedActions;")
        self.driver.quit()
        self.is_recording = False
        
        with open(f'{routine_name}_actions.json', 'w') as f:
            json.dump(self.actions, f)
        
        return f"Recording stopped. Actions saved to {routine_name}_actions.json"

# Create an instance of the Recorder class
recorder = Recorder()

if __name__ == "__main__":
    recorder.start_recording()
    input("Press Enter to stop recording...")
    recorder.stop_recording("test_routine")