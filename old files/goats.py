import os
import asyncio
from utils.helpers import click_image, wait_for_image

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')

class GOATSRoutine:
    def __init__(self, app_launcher):
        self.app_launcher = app_launcher

    async def run(self):
        # Running the routine
        print("Starting GOATS routine...")

        # Check if Chrome is already running and Telegram is launched
        if not self.app_launcher.driver:
            await self.app_launcher.launch_chrome()  # Chrome and Telegram get launched here

        await asyncio.sleep(3)  # Reduced initial wait
        await self.wait_for_login()  # Check if the user is logged in

        # Open the GOATS channel
        await self.open_goats_channel()

        # Continue the routine after entering the GOATS channel
        await self.continue_goats_routine()

    async def is_logged_in(self):
        try:
            await wait_for_image(os.path.join(BASE_PATH, 'goats', 'goats_channel_icon.png'), timeout=30)
            print("User is logged in")
            return True
        except Exception as e:
            print(f"Login check failed: {e}")
            return False

    async def wait_for_login(self):
        print("Checking login status...")
        if await self.is_logged_in():
            print("User is already logged in")
            return
        print("User is not logged in. Please log in manually.")
        login_attempts = 0
        while not await self.is_logged_in():
            await asyncio.sleep(3)
            login_attempts += 1
            if login_attempts >= 12:
                print("Login timeout. Please check the browser and try again.")
                return
        print("User logged in successfully")

    async def open_goats_channel(self):
        print("Opening GOATS channel in Telegram Web...")
        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                image_path = os.path.join(BASE_PATH, 'goats', 'goats_channel_icon.png')
                result = await click_image(image_path, timeout=30)
                if result:
                    print(f"Clicked GOATS channel icon at {result}")
                    await asyncio.sleep(3)  # Allow time for the channel to load
                    success = True
                else:
                    print(f"Failed to click GOATS channel icon (Attempt {4 - retries}/3)")
                retries -= 1
                await asyncio.sleep(5)  # Reduced retry wait time
            except Exception as e:
                print(f"Error opening the GOATS channel: {e}")

        if not success:
            print("Could not find the GOATS channel after 3 attempts.")

    async def continue_goats_routine(self):
        print("Continuing GOATS routine...")

        # Clicking the launch button
        print("Clicking Launch Button...")
        await self.click_launch_button()

        # Clicking the missions tab
        print("Clicking Missions Tab...")
        missions_clicked = await self.open_missions_tab()

        if not missions_clicked:
            print("Missions tab not clicked. Stopping the routine.")
            return  # Stop execution if missions tab is not found

        # Clicking the do button to watch an ad
        print("Clicking Do Button...")
        await self.click_do_button()

        # Simulate watching the ad for 18 seconds
        await asyncio.sleep(18)

        # Return and wait for the next cycle
        await self.wait_for_next_cycle()

    async def click_launch_button(self):
        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                image_path = os.path.join(BASE_PATH, 'goats', 'launch_button.png')
                result = await click_image(image_path, timeout=30)
                if result:
                    print(f"Clicked launch button at {result}")
                    success = True
                else:
                    print(f"Failed to click launch button (Attempt {4 - retries}/3)")
                retries -= 1
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Error clicking launch button: {e}")

    async def open_missions_tab(self):
        # Introduce a fixed 10-second wait before searching for the missions tab
        await asyncio.sleep(10)

        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                image_path = os.path.join(BASE_PATH, 'goats', 'missions_tab.png')
                result = await click_image(image_path, timeout=30)
                if result:
                    print(f"Clicked missions tab at {result}")
                    success = True
                else:
                    print(f"Failed to click missions tab (Attempt {4 - retries}/3)")
                retries -= 1
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Error clicking missions tab: {e}")

        return success  # Return success status to control the flow

    async def click_do_button(self):
        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                image_path = os.path.join(BASE_PATH, 'goats', 'do_button.png')
                result = await click_image(image_path, timeout=30)
                if result:
                    print(f"Clicked do button at {result}")
                    success = True
                else:
                    print(f"Failed to click do button (Attempt {4 - retries}/3)")
                retries -= 1
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Error clicking do button: {e}")

    async def wait_for_next_cycle(self):
        print("Waiting for the next cycle...")
        await asyncio.sleep(60)
        await self.click_home_screen()
        await self.open_missions_tab()
        await self.click_do_button()

    async def click_home_screen(self):
        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                image_path = os.path.join(BASE_PATH, 'goats', 'home_screen.png')
                result = await click_image(image_path, timeout=30)
                if result:
                    print(f"Clicked home screen at {result}")
                    success = True
                else:
                    print(f"Failed to click home screen (Attempt {4 - retries}/3)")
                retries -= 1
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Error clicking home screen: {e}")
