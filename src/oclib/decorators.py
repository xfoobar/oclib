import time
import sys
from typing import Callable, Sequence
import inspect


def timer(func: Callable):
    """
    Decorator to measure the time of a function
    :param func: function to measure
    :return: result, total time(seconds)
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        total = time.time() - start
        return result, total

    return wrapper


def retry(times: int, exceptions: Sequence[Exception] | None = None, delay: float = 0, print_error: bool = True):
    """
    Retry Decorator
    Retries the wrapped function `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function
    :param exceptions: Sequence of exceptions that trigger a retry attempt, default Exception
    :param delay: Delay between retry attempts (seconds), default 0
    :param print_error: Print error message to stderr, default True
    """

    if exceptions is None:
        exceptions = (Exception,)

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as ex:
                    attempt += 1
                    if print_error:
                        print(f'{type(ex)}:{ex} thrown when attempting to run {func}, attempt {attempt} of {times}',
                              file=sys.stderr)
                    time.sleep(delay)
            return func(*args, **kwargs)

        return wrapper

    return decorator

