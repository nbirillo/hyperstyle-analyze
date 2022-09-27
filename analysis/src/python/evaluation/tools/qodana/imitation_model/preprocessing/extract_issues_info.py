import argparse
import sys
from typing import Dict

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.templates.filter_using_diff import get_issues_with_offset
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.utils.df_utils import dict_to_df, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger


def preprocess_issues_in_submission(submission: pd.Series, issues_column: str, issues_to_ids: Dict[str, int]) \
        -> pd.Series:

    prep_submissions = submission[[SubmissionColumns.ID.value, SubmissionColumns.CODE.value]].copy()

    report = parse_report(submission, issues_column)
    code = split_code_to_lines(submission[SubmissionColumns.CODE.value], keep_ends=True)
    issues_with_offset = get_issues_with_offset(report, code)

    prep_issues = []
    for offset, issue in issues_with_offset:
        issue_name = issue.get_name()
        if issue_name not in issues_to_ids:
            issues_to_ids[issue_name] = len(issues_to_ids)

        issue_id = issues_to_ids[issue.get_name()]
        issue_line_number = issue.get_line_number()
        issue_column_number = issue.get_column_number()
        issue_offset = offset
        prep_issues.append((issue_id, issue_line_number, issue_column_number, issue_offset))

    prep_submissions[issues_column] = prep_issues

    return prep_submissions


def main(submissions_path: str, prep_submissions_path: str, issues_to_ids_path: str, issues_column: str):
    """ Create dataframe with issues names to ids mapping. """

    issues_to_ids = {}

    df_submissions = read_df(submissions_path)
    df_prep_submissions = df_submissions.apply(preprocess_issues_in_submission,
                                               issues_column=issues_column,
                                               issues_to_ids=issues_to_ids,
                                               axis=1)

    df_issues_to_ids = dict_to_df(issues_to_ids, IssuesColumns.NAME.value, IssuesColumns.ID.value)
    write_df(df_issues_to_ids, issues_to_ids_path)
    write_df(df_prep_submissions, prep_submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions')
    parser.add_argument('prep_submissions_path', type=str, help='Path to .csv file with preprocessed submissions path')
    parser.add_argument('issues_to_ids_path', type=str, help='Path to .csv file with issue to id mapping')

    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored (can be hyperstyle_issues or qodana_issues).',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.submissions_path, 'imitation_model', args.log_path)

    main(args.submissions_path,
         args.prep_submissions_path,
         args.issues_to_ids_path,
         args.issues_column)
