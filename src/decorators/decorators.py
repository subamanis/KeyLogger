import functools, time, traceback

times : dict[str,float] = dict()


def print_pending_benchmarks():
    for key in times:
        print('- {} took {} secs.'.format(key,__format_exec_time(times[key])))


def benchmark(tag, should_print_immediate=True, is_recursive=False):
    def decorator(func):
        if is_recursive:
            return __decorator_benchmark_recursive(func,tag,should_print_immediate)
        else:
            return __decorator_benchmark_normal(func,tag,should_print_immediate)
    return decorator


def __decorator_benchmark_recursive(func,tag, should_print_immediate):
    count=0
    start = time.time()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal start
        nonlocal count
        count += 1
        value = func(*args, **kwargs)
        count -= 1

        if should_print_immediate:
            __print_benchmark_info(tag, time.time() - start)
        else:
            times[tag] = time.time() - start
        return value

    return wrapper


def __decorator_benchmark_normal(func,tag,should_print_immediate):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)

        if should_print_immediate:
            __print_benchmark_info(tag, time.time() - start)
        else:
            __add_time(tag,time.time()-start)
        return value

    return wrapper


def __add_time(tag:str, exec_time):
    global times
    value = 0
    if tag in times:
        value = times[tag]
    times[tag] = value + exec_time


def catch_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc(e)
            return None

        return value

    return wrapper


def __print_tagged_benchmark_info(tag:str):
    print("- {} took {} secs.".format(tag,__format_exec_time(times[tag])))


def __print_benchmark_info(tag:str, exec_time:float):
    print("- {} took {} secs.".format(tag,__format_exec_time(exec_time)))


def __format_exec_time(exec_time) -> float:
    if exec_time > 0.099:
        return round(exec_time, 2)

    return round(exec_time, 3)
