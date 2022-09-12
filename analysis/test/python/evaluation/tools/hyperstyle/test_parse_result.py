from pathlib import Path
from typing import List

import pandas as pd
import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.tools.hyperstyle.evaluate import parse_hyperstyle_new_format_result, \
    parse_hyperstyle_result
from analysis.src.python.evaluation.tools.hyperstyle.model.report import HyperstyleReport
from analysis.test.python.evaluation.tools import HYPERSTYLE_DIR_PATH
from analysis.test.python.evaluation.tools.test_evaluation_utils.evaluation_test_utils import \
    run_evaluation_parsing_test

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


def parse_hyperstyle_issues(df: pd.Series):
    report = HyperstyleReport.from_json(df[SubmissionColumns.HYPERSTYLE_ISSUES.value])
    return report.issues


@pytest.mark.parametrize(('result_file', 'solutions_count', 'issues_count'), NEW_FORMAT_DATA)
def test_new_format(result_file: Path, solutions_count: int, issues_count: List[int]):
    run_evaluation_parsing_test(
        result_path=NEW_FORMAT_RESOURCES_PATH / result_file,
        parse_result=parse_hyperstyle_new_format_result,
        get_result_issues=parse_hyperstyle_issues,
        result_shape=solutions_count,
        result_row_shapes=issues_count)


OLD_FORMAT_DATA = [
    ('java8_result.json', 5),
    ('python3_result.json', 2),
    ('kotlin_result.json', 2),
]


@pytest.mark.parametrize(('result_file', 'issues_count'), OLD_FORMAT_DATA)
def test_old_format(result_file: Path, issues_count: int):
    run_evaluation_parsing_test(
        result_path=OLD_FORMAT_RESOURCES_PATH / result_file,
        parse_result=lambda result_path: parse_hyperstyle_result(result_path).to_frame().T,
        get_result_issues=parse_hyperstyle_issues,
        result_shape=1,
        result_row_shapes=[issues_count])
