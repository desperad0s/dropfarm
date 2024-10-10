import asyncio
from pyppeteer import launch
import json
import os
import keyboard
from pynput import mouse
import logging
from celery import shared_task

logging.basicConfig(level=logging.INFO)

@shared_task
def start_recording_task(routine_name):
    recorder = Recorder()
    return recorder.start_recording(routine_name)

class Recorder:
    def __init__(self):
        self.browser = None
        self.page = None
        self.recording = False
        self.actions = []
        self.start_time = None

    def start_recording(self, routine_name):
        if self.recording:
            return "Already recording"
        
        try:
            url = 'https://web.telegram.org/k/'  # Fixed URL for now
            
            async def run_async():
                self.browser = await launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
                self.page = await self.browser.newPage()
                await self.page.goto(url)
                
                logging.info(f"Starting recording for routine: {routine_name}")
                logging.info("Press 'r' to start recording, 's' to stop recording.")
                
                self.recording = True
                self.actions = []
                self.start_time = asyncio.get_event_loop().time()
                
                # Set up mouse listener
                self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
                self.mouse_listener.start()
                
                logging.info("Recording started. Press 's' to stop recording.")
                
                keyboard.wait('s')
                await self.stop_recording()

            asyncio.get_event_loop().run_until_complete(run_async())
            
            return f"Recording completed for routine: {routine_name}"
        except Exception as e:
            logging.exception(f"Error starting recording: {str(e)}")
            raise

    def on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            current_time = asyncio.get_event_loop().time() - self.start_time
            self.actions.append({
                'type': 'click',
                'x': x,
                'y': y,
                'time': current_time
            })
            logging.info(f"Recorded click at ({x}, {y})")

    def on_move(self, x, y):
        if self.recording:
            current_time = asyncio.get_event_loop().time() - self.start_time
            self.actions.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': current_time
            })

    def stop_recording(self):
        if not self.recording:
            return "Not currently recording"
        
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        logging.info("Recording stopped")
        return "Recording stopped"

    async def save_routine(self, routine_name):
        if not self.actions:
            return "No actions to save"
        
        file_path = os.path.join('recorded_routines', f'{routine_name}.json')
        with open(file_path, 'w') as f:
            json.dump({'actions': self.actions}, f)
        
        return f"Routine saved as {routine_name}"

    async def load_routine(self, routine_name):
        file_path = os.path.join('recorded_routines', f'{routine_name}.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.actions = data['actions']
        return f"Routine {routine_name} loaded"

    async def playback_routine(self, url):
        if not self.actions:
            return "No routine loaded or recorded"
        
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.goto(url)
        
        start_time = asyncio.get_event_loop().time()
        
        for action in self.actions:
            await asyncio.sleep(action['time'] - (asyncio.get_event_loop().time() - start_time))
            
            if action['type'] == 'click':
                await self.page.mouse.click(action['x'], action['y'])
            elif action['type'] == 'move':
                await self.page.mouse.move(action['x'], action['y'])
        
        await self.browser.close()
        self.browser = None
        self.page = None
        
        return "Routine playback completed"

    async def translate_to_headless(self, routine_name):
        await self.load_routine(routine_name)
        
        headless_actions = []
        for action in self.actions:
            if action['type'] == 'click':
                headless_actions.append({
                    'type': 'click',
                    'selector': f'document.elementFromPoint({action["x"]}, {action["y"]})',
                    'time': action['time']
                })
            elif action['type'] == 'move':
                headless_actions.append({
                    'type': 'move',
                    'selector': f'document.elementFromPoint({action["x"]}, {action["y"]})',
                    'time': action['time']
                })
        
        file_path = os.path.join('recorded_routines', f'{routine_name}_headless.json')
        with open(file_path, 'w') as f:
            json.dump({'actions': headless_actions}, f)
        
        return f"Routine translated to headless and saved as {routine_name}_headless"