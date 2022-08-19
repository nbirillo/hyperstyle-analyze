from pathlib import Path
from typing import List

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.tools.qodana.evaluate import parse_qodana_result
from analysis.src.python.evaluation.tools.qodana.model.report import QodanaReport
from analysis.test.python.evaluation import QODANA_DIR_PATH
from analysis.test.python.evaluation.utils.evaluation_test_utils import run_evaluation_parsing_test

RESOURCES_PATH = QODANA_DIR_PATH / 'parse_result'

QODANA_OUTPUT_DATA = [
    ('result-allProblems-java.json', 2, [2, 2]),
    ('result-allProblems-python.json', 1, [1]),
]


@pytest.mark.parametrize(('result_file', 'solutions_count', 'issues_count'), QODANA_OUTPUT_DATA)
def test_parse_qodana_result(result_file: Path, solutions_count: int, issues_count: List[int]):
    run_evaluation_parsing_test(
        result_path=RESOURCES_PATH / result_file,
        parse_result=parse_qodana_result,
        get_result_issues=lambda result_content:
        QodanaReport.from_json(result_content[SubmissionColumns.QODANA_ISSUES.value]).list_problem,
        result_shape=solutions_count,
        result_row_shapes=issues_count)
