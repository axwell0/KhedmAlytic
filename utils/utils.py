import logging
import time
import functools
import pymongo


def auto_reconnect(max_auto_reconnect_attempts):
    """Auto reconnect handler"""
    def decorator(mongo_op_func):
        @functools.wraps(mongo_op_func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_auto_reconnect_attempts):
                try:
                    return mongo_op_func(*args, **kwargs)
                except pymongo.errors.AutoReconnect as e:
                    wait_t = 0.5 * pow(2, attempt)
                    logging.warning("PyMongo auto-reconnecting... %s. Waiting %.1f seconds.", str(e), wait_t)
                    time.sleep(wait_t)
            raise pymongo.errors.AutoReconnect(f"Failed to reconnect after {max_auto_reconnect_attempts} attempts.")
        return wrapper
    return decorator



