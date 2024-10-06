import pyautogui
import asyncio
import os
import pyscreeze

async def click_image(image_path, confidence=0.7, minSearchTime=50, timeout=10, region=None):
    print(f"Attempting to click image: {image_path}")
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        if os.path.exists(image_path):
            try:
                x, y = pyscreeze.locateCenterOnScreen(image_path, confidence=confidence, minSearchTime=1, region=region)
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                print(f"Clicked image at ({x}, {y})")
                return True
            except TypeError:
                print("Image not found on screen")
        else:
            print(f"Image file not found: {image_path}")
        await asyncio.sleep(0.5)
    print(f"Image {image_path} not found within {timeout} seconds")
    return False

async def wait_for_image(image_path, confidence=0.4, timeout=10):
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return True
        await asyncio.sleep(0.5)
    print(f"Image {image_path} not found within {timeout} seconds")
    return False
