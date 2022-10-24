import pytest

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.templates.filter_using_diff import extract_template_issues, \
    filter_template_issues_using_diff
from analysis.src.python.utils.df_utils import equal_df, read_df
from analysis.test.python.data_analysis import TEMPLATES_ISSUES_FOLDER

TEMPLATE_ISSUES_FOLDER = TEMPLATES_ISSUES_FOLDER / 'template_issues_using_diff'

TEMPLATE_ISSUES_TEST_DATA = [
    ('submissions_python3_hyperstyle.csv', 'steps.csv',
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'filtered_submissions_python3_hyperstyle.csv'),
]


def prepare_template_issues_df(template_issues_df: pd.DataFrame) -> pd.DataFrame:
    template_issues_df = template_issues_df.reset_index(drop=True)
    template_issues_df[SubmissionColumns.STEP_ID.value] \
        = pd.to_numeric(template_issues_df[SubmissionColumns.STEP_ID.value])
    template_issues_df[IssuesColumns.POSITION.value] = pd.to_numeric(template_issues_df[IssuesColumns.POSITION.value])
    return template_issues_df


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

    template_issues_df = extract_template_issues(df_filtered_issues, issues_column)
    template_issues_df_result = read_df(TEMPLATE_ISSUES_FOLDER / 'templated_issues_df.csv')
    assert equal_df(template_issues_df_result, prepare_template_issues_df(template_issues_df))
