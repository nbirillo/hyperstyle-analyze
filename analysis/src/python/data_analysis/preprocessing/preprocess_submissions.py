import argparse
import logging
import sys
from enum import Enum, unique
from typing import Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import Client, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utils import configure_logger
from analysis.src.python.data_analysis.utils.parsing_utils import str_to_datetime


def check_same_code(submission_0: pd.Series, submission_1: pd.Series) -> bool:
    """ Check if submission not the same as previous. """

    return submission_0[SubmissionColumns.CODE.value].strip() == submission_1[SubmissionColumns.CODE.value].strip()


def check_different_code(submission_0: pd.Series, submission_1: pd.Series, diff_ratio: float) -> bool:
    """ Check if submission not so different with previous (lines number does not changed in `diff_ratio` times). """

    code_0 = submission_0[SubmissionColumns.CODE.value]
    code_1 = submission_1[SubmissionColumns.CODE.value]
    code_lines_diff = len(code_0) / len(code_1)
    return not (1 / diff_ratio <= code_lines_diff <= diff_ratio)


@unique
class SubmissionsCheckStatus(Enum):
    OK = 'ok'
    SAME = 'same'
    DIFFERENT = 'different'


def filter_submissions_series(submissions_series: pd.DataFrame, diff_ratio: float) -> pd.DataFrame:
    """ Filter submissions in submission series (group of submissions by one user on one step). """

    logging.info(f'Processing submission series group {submissions_series.iloc[0][SubmissionColumns.GROUP.value]}')
    logging.info(f'Initial group shape {submissions_series.shape}')

    status = []
    submissions_series[SubmissionColumns.TIME.value] = submissions_series[SubmissionColumns.TIME.value] \
        .apply(str_to_datetime)
    submissions_series.sort_values([SubmissionColumns.TIME.value], inplace=True)

    prev_submission = None
    attempt = 0

    for _, submission in submissions_series.iterrows():
        attempt += 1

        if prev_submission is not None:
            if check_same_code(prev_submission, submission):
                logging.info(f'Drop submission: '
                             f'user={submission[SubmissionColumns.USER_ID.value]} '
                             f'step={submission[SubmissionColumns.STEP_ID.value]} '
                             f'attempt={attempt + 1}: '
                             f'same submissions')
                status.append(SubmissionsCheckStatus.SAME.value)
                continue
            elif check_different_code(submission, submission, diff_ratio):
                logging.info(f'Drop submission: '
                             f'user={submission[SubmissionColumns.USER_ID.value]} '
                             f'step={submission[SubmissionColumns.STEP_ID.value]} '
                             f'attempt={attempt + 1}: '
                             f'different submissions')
                status.append(SubmissionsCheckStatus.DIFFERENT.value)
                continue

        prev_submission = submission
        status.append(SubmissionsCheckStatus.OK.value)

    submissions_series = submissions_series[(pd.Series(status) == SubmissionsCheckStatus.OK.value).values].copy()
    group_size = submissions_series.shape[0]
    submissions_series[SubmissionColumns.ATTEMPT.value] = list(range(1, group_size + 1))
    submissions_series[SubmissionColumns.TOTAL_ATTEMPTS.value] = [group_size] * group_size

    logging.info(f'Final group shape {submissions_series.shape}')

    return submissions_series


def filter_submissions_without_code(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Filter submissions with integer answer instead of code string. """

    df_submissions = df_submissions[df_submissions[SubmissionColumns.CODE.value].apply(lambda x: isinstance(x, str))]
    logging.info('Filter submissions without code (test cases or other)')

    return df_submissions


def filter_submissions_with_many_attempts(df_submissions: pd.DataFrame, max_attempts: int) -> pd.DataFrame:
    """ Filter submissions with more then max attempts. """

    logging.info(f'Filter submissions with > {max_attempts} attempts. Submissions shape: {df_submissions.shape}')
    df_submissions = df_submissions[df_submissions[SubmissionColumns.TOTAL_ATTEMPTS.value] <= max_attempts]
    logging.info(f'Finish filtering. Submissions shape: {df_submissions.shape}')

    return df_submissions


def get_submissions_user(df_submissions: pd.DataFrame, submissions_to_users_path: str) -> pd.DataFrame:
    """ Merges submissions with users. """

    df_submissions_to_users = read_df(submissions_to_users_path)
    logging.info(f'Submissions to user shape: {df_submissions_to_users.shape}')

    logging.info('Merging submissions with submissions to users')
    df_submissions = merge_dfs(df_submissions, df_submissions_to_users,
                               SubmissionColumns.ID.value, SubmissionColumns.ID.value)
    logging.info(f'Finish merging. Submissions shape: {df_submissions.shape}')

    return df_submissions


def get_client_tag(base_client: str) -> str:
    """ Get client tag (idea is universal tag of all ides). """

    if base_client == Client.WEB.value:
        return Client.WEB.value
    return Client.IDEA.value


def get_submissions_client(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Change client column name. """

    df_submissions[SubmissionColumns.BASE_CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value]
    logging.info(f"Set submissions base client:\n{df_submissions[SubmissionColumns.BASE_CLIENT.value].value_counts()}")
    df_submissions[SubmissionColumns.CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value] \
        .apply(get_client_tag)
    logging.info(f"Set submissions client:\n{df_submissions[SubmissionColumns.CLIENT.value].value_counts()}")

    return df_submissions


def get_submissions_group(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions[SubmissionColumns.GROUP.value] = df_submissions \
        .groupby([SubmissionColumns.USER_ID.value, SubmissionColumns.STEP_ID.value]).ngroup()

    return df_submissions


def get_submissions_attempt(df_submissions: pd.DataFrame, diff_ration: float) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions = df_submissions \
        .groupby([SubmissionColumns.GROUP.value], as_index=False) \
        .apply(lambda g: filter_submissions_series(g, diff_ration))

    df_submissions_last_attempt = df_submissions[
        df_submissions[SubmissionColumns.ATTEMPT.value] == df_submissions[SubmissionColumns.TOTAL_ATTEMPTS.value]]
    logging.info(f"Set submissions attempts:\n"
                 f"{df_submissions_last_attempt[SubmissionColumns.TOTAL_ATTEMPTS.value].value_counts()}")

    return df_submissions


def preprocess_submissions(submissions_path: str,
                           submissions_to_users_path: Optional[str],
                           preprocessed_submissions_path: str,
                           diff_ration: float,
                           max_attempts: Optional[int]):
    """ Prepare submissions dataset, merge with users information and issues, add group and attempt information,
    filter suspicious attempts and submissions series with much attempts. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial shape: {df_submissions.shape}')

    if SubmissionColumns.STEP in df_submissions.columns:
        df_submissions.rename({SubmissionColumns.STEP: SubmissionColumns.STEP_ID}, inplace=True)

    # Change client to web/idea
    df_submissions = get_submissions_client(df_submissions)
    # Filter submissions with have number of answer instead of code
    df_submissions = filter_submissions_without_code(df_submissions)

    # Add submission user_id
    if submissions_to_users_path is not None:
        df_submissions = get_submissions_user(df_submissions, submissions_to_users_path)

    # Add submission group
    df_submissions = get_submissions_group(df_submissions)
    # Add submission attempt
    df_submissions = get_submissions_attempt(df_submissions, diff_ration)
    # Filter submissions with many attempts (consider as noise)
    df_submissions = filter_submissions_with_many_attempts(df_submissions, max_attempts)

    logging.info(f'Submissions final shape: {df_submissions.shape}')
    logging.info(f'Saving submissions to {preprocessed_submissions_path}')
    write_df(df_submissions, preprocessed_submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to file with submissions')
    parser.add_argument('preprocessed_submissions_path', type=str, nargs='?', default=None,
                        help='Path to output file with submissions with issues.')
    parser.add_argument('--users-to-submissions-path', type=str, default=None,
                        help='Path to file with user/submission relation '
                             '(if data is not presented in submissions dataset or was anonymize).')
    parser.add_argument('--diff-ratio', type=float, default=10.0,
                        help='Ration to remove submissions which has lines change more then in `diff_ratio` times.')
    parser.add_argument('--max-attempts', type=int, default=5,
                        help='Remove submissions series with more then `max-attempts` attempts.')

    args = parser.parse_args(sys.argv[1:])
    if args.preprocessed_submissions_path is None:
        args.preprocessed_submissions_path = args.submissions_path

    configure_logger(args.preprocessed_submissions_path, 'preprocess')

    preprocess_submissions(args.submissions_path,
                           args.users_to_submissions_path,
                           args.preprocessed_submissions_path,
                           args.diff_ratio,
                           args.max_attempts)
