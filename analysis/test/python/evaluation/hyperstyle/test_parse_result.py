from pathlib import Path
from typing import List

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluate import parse_hyperstyle_new_format_result, \
    parse_hyperstyle_result
from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleReport
from analysis.test.python.evaluation import HYPERSTYLE_DIR_PATH

RESOURCES_PATH = HYPERSTYLE_DIR_PATH / 'parse_result'
NEW_FORMAT_RESOURCES_PATH = RESOURCES_PATH / 'new_format'
OLD_FORMAT_RESOURCES_PATH = RESOURCES_PATH / 'old_format'

NEW_FORMAT_DATA = [
    ('java8_result.json', 3, [4, 6, 5]),
    ('java11_result.json', 3, [1, 4, 0]),
    ('js_result.json', 1, [3]),
    ('python3_result.json', 3, [0, 0, 2]),
    ('kotlin_result.json', 3, [1, 2, 2]),
]


@pytest.mark.parametrize(('result_file', 'solutions_count', 'issues_count'), NEW_FORMAT_DATA)
def test_new_format(result_file: Path, solutions_count: int, issues_count: List[int]):
    df_result = parse_hyperstyle_new_format_result(NEW_FORMAT_RESOURCES_PATH / result_file)
    assert df_result.shape[0] == solutions_count
    for i, result in enumerate(df_result.iterrows()):
        report = HyperstyleReport.from_str(result[1][SubmissionColumns.HYPERSTYLE_ISSUES.value])
        assert len(report.issues) == issues_count[i]


OLD_FORMAT_DATA = [
    ('java8_result.json', 5),
    ('python3_result.json', 2),
    ('kotlin_result.json', 2),
]


@pytest.mark.parametrize(('result_file', 'issues_count'), OLD_FORMAT_DATA)
def test_old_format(result_file: Path, issues_count: int):
    result = parse_hyperstyle_result(OLD_FORMAT_RESOURCES_PATH / result_file)
    report = HyperstyleReport.from_str(result[SubmissionColumns.HYPERSTYLE_ISSUES.value])
    assert len(report.issues) == issues_count
