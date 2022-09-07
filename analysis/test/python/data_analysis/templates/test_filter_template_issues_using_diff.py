import pytest

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.templates.filter_using_diff import filter_template_issues_using_diff
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.test.python.data_analysis import TEMPLATES_ISSUES_FOLDER

TEMPLATE_ISSUES_FOLDER = TEMPLATES_ISSUES_FOLDER / 'template_issues_using_diff'

TEMPLATE_ISSUES_TEST_DATA = [
    ('submissions_python3_hyperstyle.csv', 'steps.csv',
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'filtered_submissions_python3_hyperstyle.csv'),
]


@pytest.mark.parametrize(
    ('submissions_path', 'steps_path', 'issues_column', 'result_path'),
    TEMPLATE_ISSUES_TEST_DATA,
)
def test_filter_template_issues_using_diff(submissions_path: str,
                                           steps_path: str,
                                           issues_column: str,
                                           result_path: str):
    df_submissions = read_df(TEMPLATE_ISSUES_FOLDER / submissions_path)
    df_steps = read_df(TEMPLATE_ISSUES_FOLDER / steps_path)

    df_filtered_issues = filter_template_issues_using_diff(df_submissions, df_steps, issues_column)

    df_result = read_df(TEMPLATE_ISSUES_FOLDER / result_path)
    assert equal_df(df_filtered_issues, df_result)
