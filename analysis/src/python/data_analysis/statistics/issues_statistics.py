import argparse
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.chunk_stats_utils import save_chunk
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.logging_utils import configure_logger


def calculate_chunk_issues_statistics(df_submissions: pd.DataFrame,
                                      df_issues: pd.DataFrame,
                                      issues_column: str) -> pd.DataFrame:
    """ Calculate number of each issue class in all submissions chunk. """

    issues_statistics = {
        SubmissionColumns.ID.value: df_submissions[SubmissionColumns.ID.value].values,
    }

    for issue_name in df_issues[IssuesColumns.NAME.value].values:
        issues_statistics[issue_name] = [0] * df_submissions.shape[0]

    submission_index = 0
    for _, submission_with_issues in df_submissions.iterrows():
        report = parse_report(submission_with_issues, issues_column)
        for issue in report.get_issues():
            issues_statistics[issue.get_name()][submission_index] += 1
        submission_index += 1

    return pd.DataFrame.from_dict(issues_statistics)


def get_issues_statistics(
        submissions_with_issues_path: str,
        issues_info_path: str,
        issues_column: str,
        issues_statistics_path: str,
        chunk_size: int):
    """ Calculate number of each issue class in all submissions. """

    df_issues = read_df(issues_info_path)
    logging.info(f"Processing dataframe chunk_size={chunk_size}")

    k = 0
    for df_submissions_with_issues in pd.read_csv(submissions_with_issues_path, chunksize=chunk_size):
        logging.info(f"Processing chunk: {k}")
        df_issues_statistics = calculate_chunk_issues_statistics(df_submissions_with_issues, df_issues, issues_column)

        save_chunk(df_issues_statistics, issues_statistics_path, k)
        k += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues statistics')
    parser.add_argument('issues_column', type=str, help='Type of issue to analyse',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument('--chunk-size', '-c', default=50000, type=int,
                        help='Number of groups which will be processed simultaneously')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.issues_statistics_path, 'statistics', args.log_path)

    get_issues_statistics(args.submissions_path,
                          args.issues_info_path,
                          args.issues_column,
                          args.issues_statistics_path,
                          args.chunk_size)
