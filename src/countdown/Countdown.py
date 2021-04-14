from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep
from typing import Callable


_executors:dict[str,ThreadPoolExecutor] = dict()
_conditions:dict[str,bool] = dict()


def make_and_start(tag:str, duration:float, callback: Callable[..., None]):
    global _executors,_conditions
    executor = ThreadPoolExecutor(max_workers=1)
    _conditions[tag] = True
    executor.submit(__countdown_repeating, tag, duration, callback)
    _executors[tag] = executor


def stop(tag):
    global _executors
    _conditions[tag] = False
    _executors[tag].shutdown(wait=False,cancel_futures=True)


def stop_all():
    global _executors, _conditions
    for tag in _executors:
        _conditions[tag] = False
        _executors[tag].shutdown(wait=False,cancel_futures=True)


def __countdown_repeating(tag:str, time:float, callback:Callable):
    global _conditions
    while _conditions[tag]:
        sleep(time)
        if _conditions[tag]:
            callback()




