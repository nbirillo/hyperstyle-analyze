import argparse
import logging
import sys
from typing import Dict

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.parsing_utils import str_to_dict


def get_issues(issues: str, issue_class_column: str, issue_type_column: str, issues_types: Dict[str, str]):
    """ Extracts issues classes and types from list with issue reports. """

    for issue in str_to_dict(issues):
        issues_types[issue[issue_class_column]] = issue.get(issue_type_column, 'Issues type undefined')


def get_issues_classes(issue_column_name: str,
                       issue_class_column: str,
                       issue_type_column: str,
                       submissions_with_issues_path: str,
                       issues_path: str):
    """ Extracts all issues classes and types from lists with issue reports in submissions with issues dataset. """

    logging.info(f'Reading submissions with issues from: {submissions_with_issues_path}')
    df_submissions_with_issues = read_df(submissions_with_issues_path)
    issues_types = {}

    logging.info(f'Getting issues class and type from submissions with issues dataset')
    df_submissions_with_issues[issue_column_name].apply(
        lambda d: get_issues(d, issue_class_column, issue_type_column, issues_types))

    logging.info(f'Saving issues classes and types to: {issues_path}')
    write_df(pd.DataFrame.from_dict({
        IssuesColumns.CLASS: issues_types.keys(),
        IssuesColumns.TYPE: issues_types.values()
    }), issues_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('issues-type', type=str, help='Type of issues to analyse (can be raw or qodana).',
                        choices=[SubmissionColumns.RAW_ISSUES, SubmissionColumns.QODANA_ISSUES])
    parser.add_argument('submissions-path', type=str, help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues-path', type=str, help='Path to .csv file where issues info will be saved')

    args = parser.parse_args(sys.argv[1:])

    issues_type = SubmissionColumns(args.issues_type)
    if issues_type == SubmissionColumns.QODANA_ISSUES:
        issue_class_column_name = SubmissionColumns.QODANA_ISSUE_CLASS
        issue_type_column_name = SubmissionColumns.QODANA_ISSUE_TYPE
    else:
        issue_class_column_name = SubmissionColumns.RAW_ISSUE_CLASS
        issue_type_column_name = SubmissionColumns.RAW_ISSUE_TYPE

    get_issues_classes(issues_type,
                       issue_class_column_name,
                       issue_type_column_name,
                       args.submissions_path,
                       args.issues_path)
