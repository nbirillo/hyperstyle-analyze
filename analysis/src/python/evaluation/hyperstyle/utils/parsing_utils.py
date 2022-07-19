import dataclasses
import json
from typing import Union

from dacite import from_dict

from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleFileReport, HyperstyleNewFormatReport, \
    HyperstyleReport


def parse_hyperstyle_new_format_report(report: str) -> HyperstyleNewFormatReport:
    return from_dict(data_class=HyperstyleNewFormatReport,
                     data=json.loads(report))


def parse_hyperstyle_report(report: str) -> HyperstyleReport:
    return from_dict(data_class=HyperstyleReport,
                     data=json.loads(report))


def dump_report(report: Union[HyperstyleNewFormatReport, HyperstyleReport, HyperstyleFileReport]) -> str:
    return json.dumps(dataclasses.asdict(report))
