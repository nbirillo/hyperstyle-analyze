import argparse
import json
import logging
import sys
from typing import Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import Client, SubmissionColumns
from analysis.src.python.data_analysis.preprocessing.filter_submissions import filter_submissions_series, \
    filter_submissions_with_many_attempts, filter_submissions_without_code
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, parallel_apply, read_df, rename_columns, \
    write_df
from analysis.src.python.data_analysis.utils.logging_utlis import configure_logger
from analysis.src.python.data_analysis.utils.parsing_utils import parse_qodana_issues


def merge_submissions_with_issues(df_submissions: pd.DataFrame, df_issues: pd.DataFrame,
                                  issue_columns: str) -> pd.DataFrame:
    """ Merges submissions with issues. """

    logging.info(f'Merging submissions with issues')
    df_issues = df_issues[[SubmissionColumns.ID, issue_columns, SubmissionColumns.CODE]]
    df_submissions = merge_dfs(df_submissions, df_issues, SubmissionColumns.CODE, SubmissionColumns.CODE, how='left')
    df_submissions[issue_columns] = df_submissions[issue_columns].fillna(value=json.dumps([]))
    logging.info(f'Finish merging. Submissions shape: {df_submissions.shape}')

    return df_submissions


def get_raw_issues(df_submissions: pd.DataFrame, raw_issues_path: str) -> pd.DataFrame:
    """ Add raw issues to submissions. """

    logging.info('Preprocessing raw issues')

    df_issues = read_df(raw_issues_path)
    logging.info(f'Issues shape: {df_issues.shape}')

    df_submissions = merge_submissions_with_issues(df_submissions, df_issues, SubmissionColumns.RAW_ISSUES.value)

    return df_submissions


def get_qodana_issues(df_submissions: pd.DataFrame, qodana_issues_path: str) -> pd.DataFrame:
    """ Add qodana issues to submissions. """

    logging.info('Preprocessing qodana issues')

    df_issues = read_df(qodana_issues_path)
    logging.info(f'Issues shape: {df_issues.shape}')

    df_issues = rename_columns(df_issues, columns={'inspections': SubmissionColumns.QODANA_ISSUES.value})
    df_issues = parallel_apply(df_issues, SubmissionColumns.QODANA_ISSUES.value, parse_qodana_issues)

    df_submissions = merge_submissions_with_issues(df_submissions, df_issues, SubmissionColumns.QODANA_ISSUES.value)

    return df_submissions


def get_submissions_user(df_submissions: pd.DataFrame, submissions_to_users_path: str) -> pd.DataFrame:
    """ Merges submissions with users. """

    df_submissions_to_users = read_df(submissions_to_users_path)
    logging.info(f'Submissions to user shape: {df_submissions_to_users.shape}')

    logging.info('Merging submissions with submissions to users')
    df_submissions = merge_dfs(df_submissions, df_submissions_to_users, SubmissionColumns.ID, SubmissionColumns.ID)
    logging.info(f'Finish merging. Submissions shape: {df_submissions.shape}')

    return df_submissions


def get_client_tag(base_client: str):
    """ Get client tag (idea is universal tag of all ides). """

    if base_client == Client.WEB.value:
        return Client.WEB.value
    return Client.IDEA.value


def get_submissions_client(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Change client column name. """

    df_submissions[SubmissionColumns.BASE_CLIENT] = df_submissions[SubmissionColumns.CLIENT]
    logging.info(f"Set submissions base client:\n{df_submissions[SubmissionColumns.BASE_CLIENT].value_counts()}")
    df_submissions[SubmissionColumns.CLIENT] = df_submissions[SubmissionColumns.CLIENT].apply(get_client_tag)
    logging.info(f"Set submissions client:\n{df_submissions[SubmissionColumns.CLIENT].value_counts()}")

    return df_submissions


def get_submissions_group(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions[SubmissionColumns.GROUP] = df_submissions \
        .groupby([SubmissionColumns.USER_ID, SubmissionColumns.STEP_ID]).ngroup()

    return df_submissions


def get_submissions_attempt(df_submissions: pd.DataFrame, diff_ration: float) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions = df_submissions \
        .groupby([SubmissionColumns.GROUP], as_index=False) \
        .apply(lambda g: filter_submissions_series(g, diff_ration))

    df_submissions_last_attempt = \
        df_submissions[df_submissions[SubmissionColumns.ATTEMPT == SubmissionColumns.TOTAL_ATTEMPTS]]
    logging.info(f"Set submissions attempts:\n"
                 f"{df_submissions_last_attempt[SubmissionColumns.TOTAL_ATTEMPTS].value_counts()}")

    return df_submissions


def preprocess_submissions(submissions_path: str,
                           submissions_to_users_path: Optional[str],
                           raw_issues_path: Optional[str],
                           qodana_issues_path: Optional[str],
                           preprocessed_submissions_path: str,
                           diff_ration: float,
                           max_attempts: Optional[int]):
    """ Prepare submissions dataset, merge with users information and issues, add group and attempt information,
    filter suspicious attempts and submissions series with much attemzps. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial shape: {df_submissions.shape}')

    # Change client to web/idea
    df_submissions = get_submissions_client(df_submissions)

    df_submissions = filter_submissions_without_code(df_submissions)
    logging.info(f'Filter submissions without code. Submissions shape: {df_submissions.shape}')

    # Add submission user_id
    if submissions_to_users_path is not None:
        df_submissions = get_submissions_user(df_submissions, submissions_to_users_path)

    # Add submission group
    df_submissions = get_submissions_group(df_submissions)
    # Add submission attempt
    df_submissions = get_submissions_attempt(df_submissions, diff_ration)
    # Filter submissions with many attempts (consider as noise)
    df_submissions = filter_submissions_with_many_attempts(df_submissions, max_attempts)

    # Add raw issues
    if raw_issues_path is not None:
        df_submissions = get_raw_issues(df_submissions, raw_issues_path)

    # Add qodana issues
    if qodana_issues_path is not None:
        df_submissions = get_qodana_issues(df_submissions, qodana_issues_path)

    logging.info(f'Submissions final shape: {df_submissions.shape}')
    logging.info(f'Saving submissions to {preprocessed_submissions_path}')
    write_df(df_submissions, preprocessed_submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to file with submissions')
    parser.add_argument('raw_issues_path', type=str, help='Path to file with raw issues/submission relation.')
    parser.add_argument('qodana_issues_path', type=str, help='Path to file with qodana issues/submission relation.')
    parser.add_argument('preprocessed_submissions_path', type=str, nargs='?', default=None,
                        help='Path to output file with submissions with issues.')
    parser.add_argument('--users-to-submissions-path', type=str, default=None,
                        help='Path to file with user/submission relation '
                             '(if data is not presented in submissions dataset or was anonymize).')
    parser.add_argument('--diff-ratio', '-r', type=float, default=10.0,
                        help='Ration to remove submissions which has lines change more then in `diff_ratio` times.')
    parser.add_argument('--max-attempts', '-r', type=int, default=5,
                        help='Remove submissions series with more then `max-attempts` attempts.')

    args = parser.parse_args(sys.argv[1:])
    if args.preprocessed_submissions_path is None:
        args.preprocessed_submissions_path = args.submissions_path

    configure_logger(args.preprocessed_submissions_path, 'preprocess')

    preprocess_submissions(args.submissions_path,
                           args.users_to_submissions_path,
                           args.raw_issues_path,
                           args.qodana_issues_path,
                           args.preprocessed_submissions_path,
                           args.diff_ratio,
                           args.max_attempts)
