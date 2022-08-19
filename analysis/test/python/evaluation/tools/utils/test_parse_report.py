from pathlib import Path
from typing import List

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.tools.utils.parsing_utils import parse_report
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.evaluation.tools import HYPERSTYLE_DIR_PATH, QODANA_DIR_PATH
from analysis.test.python.evaluation.tools.test_evaluation_utils.evaluation_test_utils import \
    run_evaluation_parsing_test

OUTPUT_DATA = [
    (QODANA_DIR_PATH / 'docker_evaluation' / 'out_1.csv', SubmissionColumns.QODANA_ISSUES.value,
     3, [2, 1, 2]),
    (HYPERSTYLE_DIR_PATH / 'docker_evaluation' / 'out_1.csv', SubmissionColumns.HYPERSTYLE_ISSUES.value,
     2, [0, 3]),
    (HYPERSTYLE_DIR_PATH / 'docker_evaluation' / 'out_2.csv', SubmissionColumns.HYPERSTYLE_ISSUES.value,
     5, [6, 1, 2, 3, 4]),
    (HYPERSTYLE_DIR_PATH / 'docker_evaluation' / 'out_3.csv', SubmissionColumns.HYPERSTYLE_ISSUES.value,
     12, [1, 4, 0, 4, 6, 5, 1, 2, 2, 0, 0, 2]),
]


@pytest.mark.parametrize(('result_file', 'issues_column', 'solutions_count', 'issues_count'), OUTPUT_DATA)
def test_parse_qodana_result(result_file: Path, issues_column: str, solutions_count: int, issues_count: List[int]):
    run_evaluation_parsing_test(
        result_path=result_file,
        parse_result=lambda path: read_df(path),
        get_result_issues=lambda result_content:
        parse_report(result_content, issues_column).get_issues(),
        result_shape=solutions_count,
        result_row_shapes=issues_count)
