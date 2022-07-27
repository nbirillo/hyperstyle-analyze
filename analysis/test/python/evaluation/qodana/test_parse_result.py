from pathlib import Path
from typing import List

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.qodana.evaluate import parse_qodana_result
from analysis.src.python.evaluation.qodana.model.report import QodanaReport
from analysis.test.python.evaluation import QODANA_DIR_PATH

RESOURCES_PATH = QODANA_DIR_PATH / 'parse_result'

QODANA_OUTPUT_DATA = [
    ('result-allProblems-java.json', 2, [2, 2]),
    ('result-allProblems-python.json', 1, [1]),
]


@pytest.mark.parametrize(('result_file', 'solutions_count', 'issues_count'), QODANA_OUTPUT_DATA)
def test_parse_qodana_result(result_file: Path, solutions_count: int, issues_count: List[int]):
    df_result = parse_qodana_result(RESOURCES_PATH / result_file)
    assert df_result.shape[0] == solutions_count
    for i, result in enumerate(df_result.iterrows()):
        report = QodanaReport.from_str(result[1][SubmissionColumns.QODANA_ISSUES.value])
        assert len(report.list_problem) == issues_count[i]
