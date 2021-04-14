from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep
from typing import Callable
from threading import Event


_executors:dict[str,ThreadPoolExecutor] = dict()
_events:dict[str,Event] = dict()


def make_and_start(tag:str, duration:float, callback: Callable):
    global _executors
    executor = ThreadPoolExecutor(max_workers=1)
    _events[tag] = Event()
    executor.submit(__countdown_repeating, tag, duration, callback)
    _executors[tag] = executor


def stop(tag):
    global _executors
    _executors[tag].shutdown(wait=False,cancel_futures=True)
    _events[tag].set()


def stop_all():
    global _executors
    for tag in _executors:
        _events[tag].set()
        _executors[tag].shutdown(wait=True,cancel_futures=True)


def __countdown_repeating(tag:str, time:float, callback:Callable):
    event = _events[tag]
    while not event.is_set():
        event.wait(time)
        if not event.is_set():
            callback()
