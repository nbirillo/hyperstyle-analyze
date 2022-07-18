import ast
import json
from datetime import datetime
from typing import Dict, List

from hyperstyle.src.python.review.inspectors.issue import BaseIssue

from analysis.src.python.evaluation.issues_statistics.common.raw_issue_encoder_decoder import RawIssueDecoder, \
    RawIssueEncoder
from analysis.src.python.evaluation.qodana.utils.models import QodanaIssue


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

    return datetime.fromisoformat(s)


def parse_qodana_issues(s: str) -> str:
    """ Parse qodana issues from string and . """

    return list_to_str(list(map(ast.literal_eval, ast.literal_eval(s)['issues'])))


def parse_qodana_issues_to_objects(s: str) -> List[QodanaIssue]:
    """ Parse qodana issues to list of objects. """

    return [QodanaIssue.from_json(json.dumps(i)) for i in json.loads(s)]


def parse_raw_issues_to_objects(s: str) -> List[BaseIssue]:
    """ Parse raw issues to list of objects. """

    return json.loads(s, cls=RawIssueDecoder)


def dump_raw_issues_to_str(issues: List[BaseIssue]) -> str:
    """ Dump raw issues to string. """

    return json.dumps(issues, cls=RawIssueEncoder)
