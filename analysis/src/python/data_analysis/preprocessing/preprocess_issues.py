import argparse
import logging
import sys
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.code_utils import get_code_with_issue_comment
from analysis.src.python.data_analysis.utils.report_utils import parse_report, parse_str_report
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def get_issues_info(df_submissions: pd.DataFrame, issues_column: str) -> pd.DataFrame:
    """ Extracts issues classes and types from submissions issues. """

    issues_info = {}

    def get_info(submission: pd.Series):
        try:
            report = parse_report(submission, issues_column)
            for issue in report.get_issues():
                issue_name = issue.get_name()
                if issue_name not in issues_info:
                    issues_info[issue_name] = {
                        IssuesColumns.NAME.value: issue_name,
                        IssuesColumns.COUNT.value: 0,
                        IssuesColumns.CATEGORY.value: issue.get_category(),
                        IssuesColumns.TEXT.value: issue.get_text(),
                        IssuesColumns.DIFFICULTY.value: issue.get_difficulty(),
                        IssuesColumns.CODE_SAMPLE.value: get_code_with_issue_comment(submission, issues_column,
                                                                                     issue_name=issue_name),
                    }
                issues_info[issue_name][IssuesColumns.COUNT.value] += 1
        except Exception as e:
            print(e, submission[issues_column])

    logging.info('Getting issues info from submissions')
    df_submissions.apply(get_info, axis=1)

    df_issue_infos = pd.DataFrame(list(map(lambda d: pd.Series(d), issues_info.values())),
                                  columns=[IssuesColumns.NAME.value, IssuesColumns.COUNT.value,
                                           IssuesColumns.CATEGORY.value, IssuesColumns.TEXT.value,
                                           IssuesColumns.DIFFICULTY.value, IssuesColumns.CODE_SAMPLE.value])

    return df_issue_infos.sort_values(by=IssuesColumns.COUNT.value, ascending=False)


def filter_issues(df_submissions: pd.DataFrame, issues_column: str, ignore_issue_names: List[str]) -> pd.DataFrame:
    """ Filter issues to selected as ignored. """

    def filter_issues_by_name(str_report: str) -> str:
        report = parse_str_report(str_report, issues_column)
        report.filter_issues(lambda issue: issue.get_name() not in ignore_issue_names)
        return report.to_json()

    df_submissions[issues_column] = df_submissions[issues_column].apply(filter_issues_by_name)

    return df_submissions


def preprocess_issues(submissions_path: str,
                      issues_info_path: str,
                      issues_column: str,
                      ignore_issue_names: Optional[List[str]]):
    """ Extracts all issues classes and types from lists with issue reports in submissions with issues dataset. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial shape: {df_submissions.shape}')

    if ignore_issue_names is not None:
        df_submissions = filter_issues(df_submissions, issues_column, ignore_issue_names)

    df_issues_info = get_issues_info(df_submissions, issues_column)

    write_df(df_issues_info, issues_info_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file where issues info will be saved')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored (can be hyperstyle_issues or qodana_issues).',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--ignore-issue-names', nargs='*', default=None,
                        help='Issues class name to ignore')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.issues_info_path, 'preprocess', args.log_path)

    preprocess_issues(args.submissions_path,
                      args.issues_info_path,
                      args.issues_column,
                      args.ignore_issue_names)
