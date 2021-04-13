from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from typing import Callable

dump_path = "../dumps/"
is_writing:bool = False
_thread:Thread
_thread_has_run:bool = False
_executor:ThreadPoolExecutor


def init():
    global _executor
    _executor = ThreadPoolExecutor(max_workers=1)


def shutdown():
    global _executor
    _executor.shutdown()


def log_to_file(buffer:list[str], callback:Callable=None):
    global _executor, is_writing
    _executor.submit(__log_to_file_from_thread, buffer, callback)


def __log_to_file_from_thread(buffer:list[str], callback:Callable):
    global is_writing

    is_writing = True
    with open(__get_dump_file_name(), mode="a+", encoding="utf-8") as f:
        for char in buffer:
            f.write(char)

    if callback is not None:
        callback()
    is_writing = False


def __get_dump_file_name() -> str:
    return dump_path+"logs.txt"
