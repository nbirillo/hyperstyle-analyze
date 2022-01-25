import argparse
import ast
import json
import logging
import sys
from typing import Dict, List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, rename_columns, write_df
from analysis.src.python.data_analysis.utils.logging_utlis import configure_logger
from analysis.src.python.data_analysis.utils.parsing_utils import list_to_str, parse_qodana_issues, str_to_dict


def get_issues(issues: str, issue_class_column: str, issue_type_column: str, issues_types: Dict[str, str]):
    """ Extracts issues classes and types from list with issue reports. """

    for issue in str_to_dict(issues):
        issues_types[issue[issue_class_column]] = issue.get(issue_type_column, 'Issues type undefined')


def get_issues_info(df_submissions: pd.DataFrame, issues_column: str,
                    issue_class_column: str, issue_type_column: str) -> pd.DataFrame:
    """ Extracts issues classes and types from submissions issues. """

    issues_info = {}

    logging.info(f'Getting issues class `{issue_class_column}` and type `{issue_type_column}` from submissions')
    df_submissions[issues_column].apply(get_issues,
                                        issue_class_column=issue_class_column,
                                        issue_type_column=issue_type_column,
                                        issues_types=issues_info)

    return pd.DataFrame.from_dict({
        IssuesColumns.CLASS: issues_info.keys(),
        IssuesColumns.TYPE: issues_info.values(),
    })


def filter_issues(issues: str, ignore_issue_classes: List[str], issue_class_column: str) -> str:
    """ Filter issues to selected as ignored. """

    filtered_issues = []
    for issue in ast.literal_eval(issues):
        if issue[issue_class_column] not in ignore_issue_classes:
            filtered_issues.append(issue)
    return list_to_str(filtered_issues)


def merge_submissions_with_issues(df_submissions: pd.DataFrame, df_issues: pd.DataFrame, issue_column: str,
                                  issue_class_column: str, ignore_issue_classes: Optional[List[str]]) -> pd.DataFrame:
    """ Filter and merges submissions with issues. """

    df_issues[issue_column] = df_issues[issue_column].fillna(value=json.dumps([]))

    logging.info(f'Filter issues')
    if ignore_issue_classes is not None:
        df_issues[issue_column] = df_issues[issue_column] \
            .apply(filter_issues,
                   ignore_issue_classes=ignore_issue_classes,
                   issue_class_column=issue_class_column)

    logging.info(f'Merging submissions with issues')
    df_issues = df_issues[[SubmissionColumns.ID, issue_column, SubmissionColumns.CODE]]
    df_submissions = merge_dfs(df_submissions, df_issues, SubmissionColumns.CODE, SubmissionColumns.CODE, how='left')
    df_submissions[issue_column] = df_submissions[issue_column].fillna(value=json.dumps([]))
    logging.info(f'Finish merging. Submissions shape: {df_submissions.shape}')

    return df_submissions


def preprocess_qodana_issues(df_issues: pd.DataFrame) -> pd.DataFrame:
    logging.info(f'Preprocessing qodana issues')

    df_issues = rename_columns(df_issues, columns={'inspections': SubmissionColumns.QODANA_ISSUES.value})
    df_issues[SubmissionColumns.QODANA_ISSUES.value] = df_issues[SubmissionColumns.QODANA_ISSUES.value] \
        .apply(parse_qodana_issues)
    return df_issues


def preprocess_issues(submissions_path: str,
                      issues_path: str,
                      issues_info_path: str,
                      issues_type: str,
                      ignore_issue_classes: List[str]):
    """ Extracts all issues classes and types from lists with issue reports in submissions with issues dataset. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial shape: {df_submissions.shape}')

    df_issues = read_df(issues_path)
    logging.info(f'Issues initial shape: {df_issues.shape}')

    issues_column = SubmissionColumns(issues_type)
    issue_type_column = SubmissionColumns.ISSUE_TYPE

    if issues_column == SubmissionColumns.QODANA_ISSUES.value:
        df_issues = preprocess_qodana_issues(df_issues)
        issue_class_column = SubmissionColumns.QODANA_ISSUE_CLASS
    else:
        issue_class_column = SubmissionColumns.RAW_ISSUE_CLASS

    df_submissions = merge_submissions_with_issues(df_submissions, df_issues,
                                                   issues_column, issue_class_column, ignore_issue_classes)
    df_issues_info = get_issues_info(df_submissions, issues_column, issue_class_column, issue_type_column)

    write_df(df_submissions, submissions_path)
    write_df(df_issues_info, issues_info_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('issues_type', type=str, help='Type of issues to analyse (can be raw or qodana).',
                        choices=[SubmissionColumns.RAW_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues_path', type=str, help='Path to .csv file with submissions to issues relation.')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file where issues info will be saved')

    parser.add_argument('--ignore-issue-classes', nargs='*', default=None,
                        help='Issues class name to ignore')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.issues_info_path, 'preprocess')

    preprocess_issues(args.submissions_path,
                      args.issues_path,
                      args.issues_info_path,
                      args.issues_type,
                      args.ignore_issue_classes)
