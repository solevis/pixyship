
def float_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = float(values[start_key])

    end = 0
    if values[end_key]:
        end = float(values[end_key])

    return start, end


def int_range(values, start_key, end_key):
    start = 0
    if values[start_key]:
        start = int(values[start_key])

    end = 0
    if values[end_key]:
        end = int(values[end_key])

    return start, end


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
