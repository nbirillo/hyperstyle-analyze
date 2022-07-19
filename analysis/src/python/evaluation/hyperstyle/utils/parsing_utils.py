import dataclasses
import json

from dacite import from_dict

from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleFileReport, HyperstyleReport


def parse_hyperstyle_report(report: str) -> HyperstyleReport:
    return from_dict(data_class=HyperstyleReport,
                     data=json.loads(report))


def dump_hyperstyle_report(report: HyperstyleReport) -> str:
    return json.dumps(dataclasses.asdict(report))


def parse_hyperstyle_file_report(file_report: str) -> HyperstyleFileReport:
    return from_dict(data_class=HyperstyleFileReport,
                     data=json.loads(file_report))


def dump_hyperstyle_file_report(file_report: HyperstyleFileReport) -> str:
    return json.dumps(dataclasses.asdict(file_report))
