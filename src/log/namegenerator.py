from pathlib import Path
from datetime import datetime


def __get_current_folder() -> str:
    return dump_path + datetime.today().strftime('%b-%d') + '/'


def __generate_new_name() -> str:
    global last_name_used
    file_path = __get_current_folder() + datetime.now().strftime('%H-%M-%S') + '.txt'
    last_name_used = file_path
    return file_path

dump_path = "../dumps/"
should_generate_new:bool = True
last_name_used:str = __generate_new_name()
times_used:int = 0


def get_file_name(is_dump:bool=False) -> str:
    global times_used

    __make_date_folder_if_not_exists()
    if times_used>5 and not is_dump:
        print('generated')
        times_used = 1
        return __generate_new_name()
    else:
        print('reused')
        times_used += 1
        return last_name_used


def get_screenshot_name() -> str:
    return __get_current_folder() + datetime.now().strftime('%H-%M-%S') + '.jpg'


def __make_date_folder_if_not_exists():
    Path(__get_current_folder()).mkdir(exist_ok=True)


