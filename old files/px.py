import asyncio
import os
from utils.helpers import click_image, wait_for_image
from utils.app_launcher import AppLauncher

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets')

class PXRoutine:
    def __init__(self):
        self.asset_path = os.path.join(BASE_PATH, 'px')
        self.initialized = False

    async def run(self):
        if not self.initialized:
            await self.initialize()

        while True:
            await self.main_cycle()

    async def initialize(self):
        await AppLauncher.open_px_app()
        self.initialized = True

    async def main_cycle(self):
        for _ in range(10):  # Paint 10 pixels
            await self.paint_pixel()
        await asyncio.sleep(50 * 60)  # Wait for 50 minutes

    async def paint_pixel(self):
        await click_image(os.path.join(self.asset_path, 'px_paintable_area.png'))
        # Add any additional steps needed to paint a pixel

    async def switch_tab(self):
        await click_image(os.path.join(self.asset_path, 'px_tab_switch.png'))
