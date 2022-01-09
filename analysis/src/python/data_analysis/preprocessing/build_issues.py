import argparse
import sys

import pandas as pd


def get_issues(issues, issue_class_column_name: str, issue_type_column_name: str, issues_types):
    for issue in str_to_dict(issues):
        issues_types[issue[issue_class_column_name]] = issue.get(issue_type_column_name, '')


def get_issues_classes(issue_column_name: str,
                       issue_class_column_name: str,
                       issue_type_column_name: str,
                       submissions_with_issues_path: str,
                       issues_path: str):
    df_submissions = read_df(submissions_with_issues_path)
    issues_types = {}
    df_submissions[issue_column_name].apply(
        lambda d: get_issues(d, issue_class_column_name, issue_type_column_name, issues_types))

    write_df(pd.DataFrame.from_dict({
        IssuesColumns.CLASS: issues_types.keys(),
        IssuesColumns.TYPE: issues_types.values()
    }), issues_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--issues-type', '-t', type=str, help='type of issues to analyse',
                        choices=[SubmissionColumns.RAW_ISSUES, SubmissionColumns.QODANA_ISSUES])
    parser.add_argument('--get-issues', '-i', type=str, help='path to submissions series', default=False)
    parser.add_argument('--submissions-path', '-sp', type=str, help='path to submissions series', required=True)
    parser.add_argument('--issues-path', '-p', type=str, help='path to issues info', required=True)

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
