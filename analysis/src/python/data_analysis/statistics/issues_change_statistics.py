import argparse
import logging
import sys
from typing import List

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import append_df, merge_dfs, write_df


def calculate_issues_change_statistics(df_issues_statistics: pd.DataFrame,
                                       issues_classes: List[str]):
    """ Calculate issues count diff between previous and current attempt in one submissions series. """

    df_issues_statistics = df_issues_statistics.sort_values(
        [SubmissionColumns.ATTEMPT])

    issues_change_statistics = {
        SubmissionColumns.ID: df_issues_statistics[SubmissionColumns.ID].values,
    }

    for issue_class in issues_classes:
        issues_change_statistics[issue_class] = []

    previous_submission_issues_statistics = None
    for i, submission_issues_statistics in df_issues_statistics.iterrows():
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

    df_issues_statistics = merge_dfs(
        df_submissions[[SubmissionColumns.ID, SubmissionColumns.GROUP, SubmissionColumns.ATTEMPT]],
        df_issues_statistics,
        SubmissionColumns.ID,
        SubmissionColumns.ID,
    )

    min_group = df_issues_statistics[SubmissionColumns.GROUP].min()
    max_group = df_issues_statistics[SubmissionColumns.GROUP].max()

    logging.info(f'Groups range: [{min_group}, {max_group}]')

    for i in range(min_group, max_group + 1, chunk_size):
        min_group_index, max_group_index = i, i + chunk_size - 1

        logging.info(f'Processing groups: [{min_group_index}, {max_group_index})')

        df_groups_submission_series = df_submissions[
            df_submissions[SubmissionColumns.GROUP].between(min_group_index, max_group_index, inclusive=True)]
        logging.info('Finish selection')

        df_grouped_submission_series = df_groups_submission_series.groupby([SubmissionColumns.GROUP], as_index=False)
        logging.info('Finish grouping')

        df_issues_change_statistics = df_grouped_submission_series.apply(calculate_issues_change_statistics,
                                                                         issues_classes=df_issues)
        logging.info('Finish filtering')

        df_issues_change_statistics = df_issues_change_statistics.reset_index(drop=True)
        logging.info('Finish aggregation')
        if i == 0:
            write_df(df_issues_change_statistics, issues_change_statistics_path)
        else:
            append_df(df_issues_change_statistics, issues_change_statistics_path)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with issues')
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
