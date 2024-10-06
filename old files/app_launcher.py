import os
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class AppLauncher:
    def __init__(self):
        self.driver = None

    async def launch_chrome(self):
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1280,1024")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-prompt-on-repost")
            options.add_argument("--disable-sync")
            options.add_argument("--display=:1")

            user_data_dir = os.path.expanduser('~/dropfarm_chrome_profile')  # Chrome profile path
            options.add_argument(f"user-data-dir={user_data_dir}")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Chrome launched successfully.")
            await asyncio.sleep(5)  # Wait for Chrome to load fully
            
            # Automatically open Telegram after launching Chrome
            await self.open_telegram()
        except Exception as e:
            print(f"Error launching Chrome: {e}")
            if self.driver:
                self.driver.quit()
            raise

    async def open_telegram(self):
        if self.driver:
            print("Opening Telegram Web...")
            try:
                self.driver.get("https://web.telegram.org/k/")  # This opens Telegram
                await asyncio.sleep(10)  # Wait for Telegram to load
            except Exception as e:
                print(f"Error opening Telegram: {e}")
                self.driver.save_screenshot("telegram_open_error.png")
        else:
            print("Chrome driver not initialized.")

    async def close_browser(self):
        if self.driver:
            print("Closing Chrome browser...")
            self.driver.quit()
            self.driver = None
            print("Chrome closed successfully.")
