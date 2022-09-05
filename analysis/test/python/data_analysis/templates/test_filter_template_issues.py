from typing import Optional, Union

import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.templates.filtering import filter_template_issues
from analysis.src.python.data_analysis.templates.utils.code_compare_utils import CodeComparator
from analysis.src.python.utils.df_utils import equal_df, read_df, write_df
from analysis.test.python.data_analysis import TEMPLATES_ISSUES_FOLDER

TEMPLATE_ISSUES_FOLDER = TEMPLATES_ISSUES_FOLDER / 'template_issues'

TEMPLATE_ISSUES_TEST_DATA = [
    ('template_issues_python3_hyperstyle.csv', 'submissions_python3_hyperstyle.csv', 'steps.csv',
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'edit_distance', False, False, 0, 'filtered_submissions_python3_hyperstyle.csv'),
]


@pytest.mark.parametrize(
    ('templates_issues_path', 'submissions_path', 'steps_path', 'issues_column', 'equal_type',
     'ignore_trailing_comments', 'ignore_trailing_whitespaces', 'equal_upper_bound', 'result_path'),
    TEMPLATE_ISSUES_TEST_DATA,
)
def test_filter_template_issues(templates_issues_path: str,
                                submissions_path: str,
                                steps_path: str,
                                issues_column: str,
                                equal_type: str,
                                ignore_trailing_comments: bool,
                                ignore_trailing_whitespaces: bool,
                                equal_upper_bound: Optional[Union[int, float]],
                                result_path: str):
    df_templates_issues = read_df(TEMPLATE_ISSUES_FOLDER / templates_issues_path)
    df_steps = read_df(TEMPLATE_ISSUES_FOLDER / steps_path)
    df_submissions = read_df(TEMPLATE_ISSUES_FOLDER / submissions_path)
    code_comparator = CodeComparator(equal_type, ignore_trailing_comments, ignore_trailing_whitespaces,
                                     equal_upper_bound)

    df_filtered_issues = filter_template_issues(df_templates_issues, df_submissions, df_steps, issues_column,
                                                code_comparator)
    write_df(df_filtered_issues, TEMPLATE_ISSUES_FOLDER / result_path)

    df_result = read_df(TEMPLATE_ISSUES_FOLDER / result_path)
    assert equal_df(df_filtered_issues, df_result)
