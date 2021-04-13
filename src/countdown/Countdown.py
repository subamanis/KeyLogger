from threading import Thread
from typing import Callable


threads : dict[str,Thread] = dict()

def make_and_start(tag:str, duration:float, callback: Callable[...,None]):
    threads[tag] = Thread(target=__run_thread, args=([duration, callback],))
    print('made and starting')
    threads[tag].start()


def __run_thread(arg:tuple[float,Callable[...,None]]):
    arg[1]()
    # for a in arg:
    #     print(a)



