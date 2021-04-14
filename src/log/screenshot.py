import pyautogui
from decorators.decorators import benchmark
from .namegenerator import get_screenshot_name


@benchmark("screenshot")
def take_screenshot():
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(get_screenshot_name())