import sys
import asyncio

# Add the correct path for imports
sys.path.append('/root/dropfarm/bot/utils')
sys.path.append('/root/dropfarm/bot/routines')

# Import the necessary classes
from app_launcher import AppLauncher
from dropfarm import Dropfarm
from goats import GOATSRoutine  # Assuming goats.py contains the routine

# Main function for testing the routine
async def test_goats_routine():
    launcher = AppLauncher()
    routine = GOATSRoutine(launcher)  # Initialize GOATSRoutine with the AppLauncher
    bot = Dropfarm(launcher, routine)  # Pass both launcher and routine to Dropfarm
    await bot.start()  # Start the GOATS routine

# Run the routine
asyncio.run(test_goats_routine())
