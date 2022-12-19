import inspect
from loguru import logger
from datetime import datetime
from functools import wraps


def cache(ttl: int = 5):
    def decorator(func):
        decorator_cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            inspect_stack = inspect.stack()
            name_func = inspect_stack[1].function
            key = kwargs.get(list(kwargs.keys())[0], "")
            time = f'{name_func}_time:{key}'
            name_and_value_func = f'{name_func}:{key}'
            if name_and_value_func not in decorator_cache and \
                    time not in decorator_cache or \
                    (datetime.utcnow() - decorator_cache[time]).seconds > ttl:
                decorator_cache[time] = datetime.utcnow()
                decorator_cache[name_and_value_func] = func(*args, **kwargs)

                logger.debug("Saving result in cache function({}) - {}...".format(
                    name_and_value_func, decorator_cache[name_and_value_func][:50]))

            logger.debug("Get result with cache function({}) - {}...".format(
                name_and_value_func, decorator_cache[name_and_value_func][:50]))

            return decorator_cache[name_and_value_func]

        return wrapper

    return decorator
