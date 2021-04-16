from .namegenerator import get_file_name
from concurrent.futures._base import Future
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from typing import Callable

_thread:Thread
_thread_has_run:bool = False
_executor:ThreadPoolExecutor
_current_future:Future


def init():
    global _executor
    _executor = ThreadPoolExecutor(max_workers=1)


def shutdown():
    global _executor
    _executor.shutdown()


def log_to_file(buffer:list[str], elements_to_skip:int=0, is_dump:bool=False, callback:Callable=None):
    global _executor, _current_future
    _current_future = _executor.submit(__log_to_file_from_thread, buffer, elements_to_skip, is_dump)
    if callback is not None:
        _current_future.add_done_callback(callback)


def __log_to_file_from_thread(buffer:list[str], elements_to_skip:bool, is_dump:bool):
    with open(get_file_name(is_dump), mode="a+", encoding="utf-8") as f:
        count = 0
        elements_to_write = len(buffer) - elements_to_skip
        for char in buffer:
            if count == elements_to_write: break
            f.write(char)
            count += 1


def queue_callback(callback:Callable):
    global _current_future
    try:
        _current_future.add_done_callback(callback)
    except Exception:
        callback()
