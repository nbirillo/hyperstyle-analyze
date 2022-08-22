from typing import Callable, List, Tuple

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.templates.search_repetitive_issues import get_repetitive_issues
from analysis.src.python.data_analysis.templates.template_matching import equal_char_by_char
from analysis.src.python.utils.df_utils import read_df
from analysis.test.python.data_analysis import TEMPLATES_ISSUES_FOLDER

REPETITIVE_ISSUES_FOLDER = TEMPLATES_ISSUES_FOLDER / 'repetitive_issues'
LINES_TEST_DATA = [
    ('in_1_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     equal_char_by_char, [('WPS446', 'e = 2.718281828459045', 0)]),
    ('in_2_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     equal_char_by_char, [('WPS446', 'e = 2.718281828459045', 0),
                          ('WPS237', 'print(f"{e:.5f}")', None)]),
    ('in_3_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     equal_char_by_char, [('WPS446', 'e = 2.718281828459045', 0)]),
]


@pytest.mark.parametrize(
    ('submission_series_path', 'template_lines', 'issues_column', 'equal', 'repetitive_issues'),
    LINES_TEST_DATA,
)
def test_get_repetitive_issues(submission_series_path: str,
                               template_lines: List[str],
                               issues_column: str,
                               equal: Callable[[str, str], bool],
                               repetitive_issues: List[Tuple[str, int]]):
    df_submission_series = read_df(REPETITIVE_ISSUES_FOLDER / submission_series_path)
    actual_repetitive_issues = get_repetitive_issues(df_submission_series, template_lines, issues_column, equal)

    assert set(actual_repetitive_issues) == set(repetitive_issues)
