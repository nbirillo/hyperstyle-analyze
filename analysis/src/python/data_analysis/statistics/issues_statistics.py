import argparse
import ast
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df
from analysis.src.python.data_analysis.utils.logging_utlis import configure_logger
from analysis.src.python.data_analysis.utils.statistics_utils import save_chunk


def calculate_chunk_issues_statistics(df_submissions: pd.DataFrame,
                                      df_issues: pd.DataFrame,
                                      issue_column: str,
                                      issue_class_column: str) -> pd.DataFrame:
    """ Calculate number of each issue class in all submissions chunk. """

    issues_statistics = {
        SubmissionColumns.ID.value: df_submissions[SubmissionColumns.ID.value].values,
    }

    for issue_class in df_issues[IssuesColumns.CLASS.value].values:
        issues_statistics[issue_class] = [0] * df_submissions.shape[0]

    k = 0
    for _, submission_with_issues in df_submissions.iterrows():
        for issue in ast.literal_eval(submission_with_issues[issue_column]):
            issues_statistics[issue[issue_class_column]][k] += 1
        k += 1

    return pd.DataFrame.from_dict(issues_statistics)


def get_issues_statistics(
        submissions_with_issues_path: str,
        issues_info_path: str,
        issues_type: str,
        issues_statistics_path: str,
        chunk_size: int):
    """ Calculate number of each issue class in all submissions. """

    df_issues = read_df(issues_info_path)
    logging.info(f"Processing dataframe chunk_size={chunk_size}")

    issue_column = SubmissionColumns(issues_type).value
    if issue_column == SubmissionColumns.QODANA_ISSUES.value:
        issue_class_key = SubmissionColumns.QODANA_ISSUE_CLASS.value
    else:
        issue_class_key = SubmissionColumns.RAW_ISSUE_CLASS.value

    k = 0
    for df_submissions_with_issues in pd.read_csv(submissions_with_issues_path, chunksize=chunk_size):
        logging.info(f"Processing chunk: {k}")
        df_issues_statistics = calculate_chunk_issues_statistics(df_submissions_with_issues, df_issues,
                                                                 issue_column, issue_class_key)

        save_chunk(df_issues_statistics, issues_statistics_path, k)
        k += 1


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('issues_type', type=str, help='Type of issue to analyse',
                        choices=[SubmissionColumns.RAW_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues statistics')
    parser.add_argument('--chunk-size', '-c', default=50000, type=int,
                        help='Number of groups which will be processed simultaneously')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.issues_statistics_path, 'statistics')

    get_issues_statistics(args.submissions_path,
                          args.issues_info_path,
                          args.issues_type,
                          args.issues_statistics_path,
                          args.chunk_size)
