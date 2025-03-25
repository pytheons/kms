from functools import wraps
from os import makedirs
from os.path import dirname


def mkdir(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        filename = None
        for arg in args:
            filename = arg.filename
            break

        makedirs(dirname(filename), exist_ok=True)
        return func(*args, **kwargs)

    return wrapper