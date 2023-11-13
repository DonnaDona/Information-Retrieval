def datestr_to_iso(datestr):
    """
    Convert date string to ISO format.

    :param datestr: date string in the format "Month day, Year"
    :return: date string in ISO format
    """
    from datetime import datetime
    date = datetime.strptime(datestr, '%B %d, %Y')
    return date.isoformat()


def parse_duration(duration_str: str) -> int:
    """
    Parse a duration string, returning the duration in minutes.

    :param duration_str: the duration string, e.g. "1 h 30 min"
    :return: the duration in minutes
    """
    parts = duration_str.split()
    hours = int(parts[0])
    minutes = int(parts[2])

    tot_minutes = hours * 60 + minutes
    return tot_minutes


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

