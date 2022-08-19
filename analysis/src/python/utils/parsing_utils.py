import json
from datetime import datetime
from typing import Dict, List

import dateutil.parser


def str_to_dict(s: str) -> Dict:
    """ Load dict from string. """

    return json.loads(s)


def dict_to_str(d: Dict) -> str:
    """ Dump dict to string. """

    return json.dumps(d)


def list_to_str(ls: List) -> str:
    """ Dump dict to string. """

    return json.dumps(ls)


def str_to_datetime(s) -> datetime:
    """ Parse datetime from string. """

    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return dateutil.parser.isoparse(s)
