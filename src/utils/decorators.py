_instances = {}

def singleton(cls):
    def wrapper(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return wrapper

# This allows importing _instances from outside
__all__ = ["singleton", "_instances"]
