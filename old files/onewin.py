import asyncio
import os
from utils.helpers import click_image, wait_for_image
from utils.app_launcher import AppLauncher

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')

class OneWinRoutine:
    def __init__(self):
        self.asset_path = os.path.join(BASE_PATH, 'onewin')
        self.initialized = False

    async def run(self):
        if not self.initialized:
            await self.initialize()

        while True:
            await self.main_cycle()

    async def initialize(self):
        await AppLauncher.open_1win_chat()
        self.initialized = True

    async def main_cycle(self):
        await self.click_launch_app()
        await self.click_claim()
        await self.exit_app()
        await asyncio.sleep(3 * 60 * 60)  # Wait for 3 hours

    async def click_launch_app(self):
        await click_image(os.path.join(self.asset_path, '1win_launch_button.png'))

    async def click_claim(self):
        await click_image(os.path.join(self.asset_path, '1win_claim_button.png'))

    async def exit_app(self):
        await click_image(os.path.join(self.asset_path, '1win_exit_button.png'))
