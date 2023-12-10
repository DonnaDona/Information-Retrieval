def try_float(s: str) -> float:
    """
    Try to convert a string to a float, returning NaN if the conversion fails.

    :param s: the string
    :return: the float
    """
    if not s:
        return float('nan')
    try:
        return float(s)
    except:
        return float('nan')


def parse_duration(duration_str: str) -> int:
    """
    Parse a duration string, returning the duration in minutes.

    :param duration_str: the duration string, e.g. "1 h 30 min"
    :return: the duration in minutes
    """
    if not duration_str:
        return -1

    parts = duration_str.split()
    if len(parts) < 4:
        if "minutes" in duration_str or "m" in duration_str:
            return int(parts[0])
        else:
            return int(parts[0]) * 60

    hours = int(parts[0])
    minutes = int(parts[2])

    tot_minutes = hours * 60 + minutes
    return tot_minutes


def try_func(func):
    try:
        return func()
    except:
        return None


class AtomicId:
    """
    A class that generates unique IDs.
    """

    def __init__(self):
        import threading
        self._id = 0
        self._lock = threading.Lock()

    def next(self):
        """
        Return the next ID.
        :return: the next ID
        """
        with self._lock:
            self._id += 1
            return self._id
