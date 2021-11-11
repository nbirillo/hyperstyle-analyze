import datetime
from typing import Optional


def str_to_datetime(date_string: Optional[str]) -> Optional[datetime.datetime]:
    """ Transform time string from platform in format `2013-07-12T07:00:00Z` to datetime. """
    if date_string is None:
        return None
    try:
        timestamp = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        timestamp = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    return timestamp
