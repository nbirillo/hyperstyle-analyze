import argparse
import logging
import sys
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.report_utils import parse_str_report
from analysis.src.python.utils.df_utils import dict_to_df, merge_dfs, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_issues_info(df_submissions: pd.DataFrame, issues_column: str) -> pd.DataFrame:
    """ Extracts issues classes and types from submissions issues. """

    issues_info = {}

    def get_info(str_report: str):
        report = parse_str_report(str_report, issues_column)
        for issue in report.get_issues():
            issues_info[issue.get_name()] = issue.get_category()

    logging.info('Getting issues names and categories from submissions')
    df_submissions[issues_column].apply(get_info)

    return dict_to_df(issues_info, IssuesColumns.NAME.value, IssuesColumns.CATEGORY.value)


def filter_issues(df_submissions: pd.DataFrame, issues_column: str, ignore_issue_names: List[str]) -> pd.DataFrame:
    """ Filter issues to selected as ignored. """

    def filter_issues_by_name(str_report: str) -> str:
        report = parse_str_report(str_report, issues_column)
        report.filter_issues(lambda issue: issue.get_name() not in ignore_issue_names)
        return report.to_json()

    df_submissions[issues_column] = df_submissions[issues_column].apply(filter_issues_by_name)

    return df_submissions


def merge_submissions_with_issues(df_submissions: pd.DataFrame,
                                  df_issues: pd.DataFrame,
                                  issues_column: str) -> pd.DataFrame:
    """ Filter and merges submissions with issues. """

    logging.info('Merging submissions with issues')
    df_issues = df_issues[[SubmissionColumns.ID.value, issues_column, SubmissionColumns.CODE.value]]
    df_submissions = merge_dfs(df_submissions, df_issues, SubmissionColumns.ID.value, SubmissionColumns.ID.value)
    logging.info(f'Finish merging. Submissions shape: {df_submissions.shape}')

    return df_submissions


def preprocess_issues(submissions_path: str,
                      issues_path: str,
                      issues_info_path: str,
                      issues_column: str,
                      ignore_issue_names: Optional[List[str]]):
    """ Extracts all issues classes and types from lists with issue reports in submissions with issues dataset. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial shape: {df_submissions.shape}')

    df_issues = read_df(issues_path)
    logging.info(f'Issues initial shape: {df_issues.shape}')

    df_submissions = merge_submissions_with_issues(df_submissions, df_issues, issues_column)

    if ignore_issue_names is not None:
        df_submissions = filter_issues(df_submissions, issues_column, ignore_issue_names)

    df_issues_info = get_issues_info(df_submissions, issues_column)

    write_df(df_submissions, submissions_path)
    write_df(df_issues_info, issues_info_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored (can be hyperstyle_issues or qodana_issues).',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues_path', type=str, help='Path to .csv file with submissions to issues relation.')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file where issues info will be saved')
    parser.add_argument('--ignore-issue-names', nargs='*', default=None,
                        help='Issues class name to ignore')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.issues_info_path, 'preprocess', args.log_path)

    preprocess_issues(args.submissions_path,
                      args.issues_path,
                      args.issues_info_path,
                      args.issues_column,
                      args.ignore_issue_names)
