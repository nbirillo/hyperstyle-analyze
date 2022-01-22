import argparse
import ast
import logging
import sys
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df
from analysis.src.python.data_analysis.utils.statistics_utils import save_chunk


def calculate_chunk_issues_statistics(df_submissions: pd.DataFrame,
                                      issues_classes: List[str],
                                      issue_column_name: str,
                                      issue_class_key: str) -> pd.DataFrame:
    """ Calculate number of each issue class in all submissions chunk. """

    issues_statistics = {
        SubmissionColumns.ID: df_submissions[SubmissionColumns.ID].values,
    }

    for issue_class in issues_classes:
        issues_statistics[issue_class] = [0] * df_submissions.shape[0]

    for i, submission_with_issues in df_submissions.iterrows():
        for issue in ast.literal_eval(submission_with_issues[issue_column_name]):
            issues_statistics[issue[issue_class_key]][i] += 1

    return pd.DataFrame.from_dict(issues_statistics)


def get_issues_statistics(
        submissions_with_issues_path: str,
        issues_path: str,
        issue_column_name: str,
        issue_class_key: str,
        issues_statistics_path: str,
        chunk_size: int):
    """ Calculate number of each issue class in all submissions. """

    df_issues = read_df(issues_path)[IssuesColumns.CLASS].values
    logging.info(f"Processing dataframe chunk_size={chunk_size}")

    k = 0
    for df_submissions_with_issues in pd.read_csv(submissions_with_issues_path, chunksize=chunk_size):
        logging.info(f"Processing chunk: {k}")
        df_issues_statistics = calculate_chunk_issues_statistics(df_submissions_with_issues, df_issues,
                                                                 issue_column_name, issue_class_key)

        save_chunk(df_issues_statistics, issues_statistics_path, k)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_type', type=str, help='Type of issue to analyse',
                        choices=[SubmissionColumns.RAW_ISSUES, SubmissionColumns.QODANA_ISSUES])
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues statistics')
    parser.add_argument('--chunk-size', '-c', default=50000, type=int,
                        help='Number of groups which will be processed simultaneously')

    args = parser.parse_args(sys.argv[1:])

    issues_type = SubmissionColumns(args.issues_type)
    if issues_type == SubmissionColumns.QODANA_ISSUES:
        issue_class_key = SubmissionColumns.QODANA_ISSUE_CLASS
    else:
        issue_class_key = SubmissionColumns.RAW_ISSUE_CLASS

    get_issues_statistics(args.submissions_path,
                          args.issues_path,
                          issues_type,
                          issue_class_key,
                          args.issues_statistics_path,
                          args.chunk_size)
