import argparse
import sys
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.utils.df_utils import merge_dfs
from analysis.src.python.utils.logging_utils import configure_logger
from analysis.src.python.data_analysis.utils.chunk_stats_utils import get_statistics_by_chunk


def calculate_issues_change_statistics(df_issues_statistics: pd.DataFrame,
                                       issue_names: List[str]):
    """ Calculate issues count diff between previous and current attempt in one submissions series. """

    df_issues_statistics = df_issues_statistics.sort_values([SubmissionColumns.ATTEMPT.value])

    issues_change_statistics = {
        SubmissionColumns.ID.value: df_issues_statistics[SubmissionColumns.ID.value].values,
    }

    for issue_name in issue_names:
        issues_change_statistics[issue_name] = []

    previous_submission_issues_statistics = None
    for _, submission_issues_statistics in df_issues_statistics.iterrows():
        for issue_name in issue_names:
            if previous_submission_issues_statistics is None:
                diff = submission_issues_statistics[issue_name]
            else:
                diff = submission_issues_statistics[issue_name] - previous_submission_issues_statistics[issue_name]

            issues_change_statistics[issue_name].append(diff)
        previous_submission_issues_statistics = submission_issues_statistics
    return pd.DataFrame.from_dict(issues_change_statistics)


def get_submissions_issues_change_statistics(submissions_path: str,
                                             issues_statistics_path: str,
                                             issues_change_statistics_path: str,
                                             issues_path: str,
                                             chunk_size=20000):
    """ Calculate issues count diff between previous and current attempt in all submissions series. """

    df_submissions = pd.read_csv(submissions_path)
    df_issues_statistics = pd.read_csv(issues_statistics_path)
    df_issues = pd.read_csv(issues_path)

    issue_names = df_issues[IssuesColumns.NAME.value].values

    df_submissions = merge_dfs(
        df_submissions[[SubmissionColumns.ID.value, SubmissionColumns.GROUP.value, SubmissionColumns.ATTEMPT.value]],
        df_issues_statistics,
        SubmissionColumns.ID.value,
        SubmissionColumns.ID.value,
    )

    get_statistics_by_chunk(df_submissions, issues_change_statistics_path, chunk_size,
                            lambda submission_series:
                            calculate_issues_change_statistics(submission_series, issue_names))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues count statistics')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_change_statistics_path', type=str,
                        help='Path to .csv file with submissions issues statistics')

    parser.add_argument('--chunk-size', '-c', default=5000, type=int,
                        help='Number of groups which will be processed simultaneously')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.issues_change_statistics_path, 'statistics', args.log_path)

    get_submissions_issues_change_statistics(args.submissions_path,
                                             args.issues_statistics_path,
                                             args.issues_change_statistics_path,
                                             args.issues_info_path,
                                             args.chunk_size)
