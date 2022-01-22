import argparse
import logging
import sys
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs
from analysis.src.python.data_analysis.utils.statistics_utils import get_statistics_by_group


def calculate_issues_change_statistics(df_issues_statistics: pd.DataFrame,
                                       issues_classes: List[str]):
    """ Calculate issues count diff between previous and current attempt in one submissions series. """

    df_issues_statistics = df_issues_statistics.sort_values([SubmissionColumns.ATTEMPT])

    issues_change_statistics = {
        SubmissionColumns.ID: df_issues_statistics[SubmissionColumns.ID].values,
    }

    for issue_class in issues_classes:
        issues_change_statistics[issue_class] = []

    previous_submission_issues_statistics = None
    for _, submission_issues_statistics in df_issues_statistics.iterrows():
        for issue_class in issues_classes:
            if previous_submission_issues_statistics is None:
                diff = submission_issues_statistics[issue_class]
            else:
                diff = submission_issues_statistics[issue_class] - previous_submission_issues_statistics[issue_class]

            issues_change_statistics[issue_class].append(diff)
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
    df_issues = pd.read_csv(issues_path)[IssuesColumns.CLASS].values

    df_submissions = merge_dfs(
        df_submissions[[SubmissionColumns.ID, SubmissionColumns.GROUP, SubmissionColumns.ATTEMPT]],
        df_issues_statistics,
        SubmissionColumns.ID,
        SubmissionColumns.ID,
    )

    get_statistics_by_group(df_submissions, issues_change_statistics_path, chunk_size,
                            lambda submission_series: submission_series.apply(calculate_issues_change_statistics,
                                                                              issues_classes=df_issues))


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues count statistics')
    parser.add_argument('issues_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_change_statistics_path', type=str,
                        help='Path to .csv file with submissions issues statistics')
    parser.add_argument('--chunk-size', '-c', default=5000, type=int,
                        help='Number of groups which will be processed simultaneously')

    args = parser.parse_args(sys.argv[1:])
    get_submissions_issues_change_statistics(args.submissions_path,
                                             args.issues_statistics_path,
                                             args.issues_change_statistics_path,
                                             args.issues_path,
                                             args.chunk_size)
