import pyautogui
import decorators.decorators
from .namegenerator import get_screenshot_name


@decorators.decorators.benchmark("screenshot")
def take_screenshot():
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(get_screenshot_name())