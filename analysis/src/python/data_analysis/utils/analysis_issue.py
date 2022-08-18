import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleReport
from analysis.src.python.evaluation.model.report import BaseReport
from analysis.src.python.evaluation.qodana.model.report import QodanaReport


def parse_str_report(str_report: str, column: str) -> BaseReport:
    if column == SubmissionColumns.HYPERSTYLE_ISSUES.value:
        return HyperstyleReport.from_json(str_report)
    if column == SubmissionColumns.QODANA_ISSUES.value:
        return QodanaReport.from_json(str_report)

    raise NotImplementedError(f'Implement parser for issue stored in column: {column}')


def parse_report(row: pd.Series, column: str) -> BaseReport:
    return parse_str_report(row[column], column)
