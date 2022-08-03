import argparse
import logging
import os
import sys
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import IssuesColumns, StepsStatsColumns, SubmissionColumns
from analysis.src.python.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger
from analysis.src.python.utils.file_utils import create_directory
from analysis.src.python.utils.extension_utils import AnalysisExtension


def get_step_to_issues_statistics(df_submissions_to_issues: pd.DataFrame, min_ratio: float = 0.1) -> pd.DataFrame:
    step_id = df_submissions_to_issues[SubmissionColumns.STEP_ID.value].iloc[0]
    df_submissions_to_issues = df_submissions_to_issues.drop(SubmissionColumns.STEP_ID.value, axis=1)

    df_issues_to_submissions = df_submissions_to_issues.transpose(copy=True) \
        .rename_axis(StepsStatsColumns.ISSUE.value) \
        .reset_index()

    df_stats = df_issues_to_submissions[[StepsStatsColumns.ISSUE.value]].copy()
    df_stats[SubmissionColumns.STEP_ID.value] = [step_id] * df_stats.shape[0]
    df_stats[StepsStatsColumns.TOTAL_COUNT.value] = [df_submissions_to_issues.shape[0]] * df_stats.shape[0]
    df_stats[StepsStatsColumns.WITH_ISSUE_COUNT.value] = df_issues_to_submissions \
        .drop(StepsStatsColumns.ISSUE.value, axis=1) \
        .applymap(lambda x: 1 if x > 0 else 0) \
        .sum(axis=1)
    df_stats[StepsStatsColumns.RATIO.value] = df_stats[StepsStatsColumns.WITH_ISSUE_COUNT.value] / df_stats[
        StepsStatsColumns.TOTAL_COUNT.value]
    df_stats[StepsStatsColumns.RATIO.value] = df_stats[StepsStatsColumns.RATIO.value].round(2)
    df_stats = df_stats[df_stats[StepsStatsColumns.RATIO.value] >= min_ratio]
    df_stats.sort_values([StepsStatsColumns.RATIO.value, StepsStatsColumns.WITH_ISSUE_COUNT.value],
                         inplace=True, ascending=False)

    return df_stats


def save_stats_unit_by_feature(df_stats: pd.DataFrame, feature: str, directory_path: str):
    feature_value = df_stats[feature].iloc[0]
    df_stats = df_stats.sort_values(StepsStatsColumns.RATIO.value, ascending=False)
    feature_stats_path = os.path.join(directory_path, f'{feature_value}{AnalysisExtension.CSV.value}')
    write_df(df_stats[df_stats.columns[~df_stats.columns.isin([feature])]], feature_stats_path)


def save_stats_by_feature(df_stats: pd.DataFrame, feature: str, base_path: str, filename: str):
    create_directory(base_path)
    stats_path = os.path.join(base_path, f'{filename}{AnalysisExtension.CSV.value}')

    df_stats = df_stats.sort_values([feature, StepsStatsColumns.RATIO.value], ascending=[True, False])
    write_df(df_stats, stats_path)

    stats_by_feature_path = os.path.join(base_path, filename)
    df_stats.groupby(SubmissionColumns.STEP_ID.value) \
        .apply(save_stats_unit_by_feature, feature=feature, directory_path=stats_by_feature_path)


def get_steps_to_issues_statistics(base_path: str, df_issues_statistics: pd.DataFrame):
    """ Calculate issue statistics for each step. """

    df_steps_count = df_issues_statistics[SubmissionColumns.STEP_ID.value].value_counts().reset_index()
    df_steps_count.columns = [SubmissionColumns.STEP_ID.value, StepsStatsColumns.TOTAL_COUNT.value]
    write_df(df_steps_count, os.path.join(base_path, 'steps_count.csv'))

    df_step_to_issues_stats = df_issues_statistics \
        .groupby([SubmissionColumns.STEP_ID.value], as_index=False) \
        .apply(get_step_to_issues_statistics)

    save_stats_by_feature(df_step_to_issues_stats,
                          SubmissionColumns.STEP_ID.value,
                          base_path,
                          'steps_to_issues')

    save_stats_by_feature(df_step_to_issues_stats,
                          StepsStatsColumns.ISSUE.value,
                          base_path,
                          'issues_to_steps')


def get_issues_steps_statistics(submissions_path: str,
                                issue_statistics_path: str,
                                issues_steps_statistics_directory_path: str,
                                issues_path: str,
                                attempt_number: Optional[int],
                                ignore_issues: List[str]):
    """ Calculate issue statistics for each step. """
    create_directory(issues_steps_statistics_directory_path)

    df_submissions = read_df(submissions_path)

    # Select submission's attempt
    if attempt_number is not None:
        if attempt_number == -1:
            df_submissions = df_submissions[
                df_submissions[SubmissionColumns.ATTEMPT.value] == SubmissionColumns.TOTAL_ATTEMPTS.value]
        else:
            df_submissions = df_submissions[df_submissions[SubmissionColumns.ATTEMPT.value] == attempt_number]

    df_issues = read_df(issues_path)
    df_issues_statistics = read_df(issue_statistics_path)

    df_issues_statistics = merge_dfs(
        df_submissions[[SubmissionColumns.ID.value, SubmissionColumns.STEP_ID.value]],
        df_issues_statistics,
        SubmissionColumns.ID.value,
        SubmissionColumns.ID.value,
    )

    df_issues = df_issues[~df_issues[IssuesColumns.NAME.value].isin(
        ignore_issues) & df_issues[IssuesColumns.NAME.value].isin(
        df_issues_statistics.columns)]

    df_issues_statistics = df_issues_statistics[
        [SubmissionColumns.STEP_ID.value] + df_issues[IssuesColumns.NAME.value].values.tolist()]

    get_steps_to_issues_statistics(issues_steps_statistics_directory_path, df_issues_statistics)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('issues_statistics_path', type=str,
                        help='Path to .csv file with submissions issues count statistics')
    parser.add_argument('issues_info_path', type=str, help='Path to .csv file with issues list (classes and types)')
    parser.add_argument('issues_steps_statistics_directory_path', type=str,
                        help='Path to directory where to save issues steps statistics for each issue class')
    parser.add_argument('--attempt-number', type=Optional[int], default=None,
                        help='Number of attempt to analyze (None --all, 1 -- first, -1 --last, and other)')
    parser.add_argument('--ignore-issues', type=str, nargs='*', default=[],
                        help='Issues class name to ignore')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.issues_steps_statistics_directory_path, 'statistics', args.log_path)

    get_issues_steps_statistics(args.submissions_path,
                                args.issues_statistics_path,
                                args.issues_steps_statistics_directory_path,
                                args.issues_info_path,
                                args.attempt_number,
                                args.ignore_issues)
