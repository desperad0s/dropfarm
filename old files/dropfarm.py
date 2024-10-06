class Dropfarm:
    def __init__(self, app_launcher, routine):
        self.app_launcher = app_launcher
        self.routine = routine

    async def start(self):
        # Launch Chrome
        await self.app_launcher.launch_chrome()

        # Start the routine (GOATS)
        await self.routine.run()
