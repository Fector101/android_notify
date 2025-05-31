"""Collection of useful functions"""

import inspect
def can_accept_arguments(func, *args, **kwargs):
    try:
        sig = inspect.signature(func)
        sig.bind(*args, **kwargs)
        return True
    except TypeError:
        return False


def run_on_ui_thread(func):
    """Fallback for Developing on PC"""
    def wrapper(*args, **kwargs):
        # print("Simulating run on UI thread")
        return func(*args, **kwargs)
    return wrapper