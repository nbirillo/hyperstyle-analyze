import argparse
import logging
import os
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns, TopicColumns, \
    UserColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.evaluation.common.file_util import create_directory, get_name_from_path


def save_to_directory(df: pd.DataFrame, path: str, directory_path: str):
    """ Save dataframe to new directory. """

    write_df(df, os.path.join(directory_path, get_name_from_path(path)))


def filter_dataset(submissions_path: str, steps_path: str, topics_path: str, users_path: str,
                   result_directory_path: str, max_attempts: int):
    """ Create directory with result dataset to analyse. Filter submissions with more then `max_attempts`. """

    create_directory(result_directory_path)
    logging.basicConfig(filename=os.path.join(result_directory_path, 'filter_dataset.log'), level=logging.DEBUG)

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial count: {df_submissions.shape[0]}')
    df_steps = read_df(steps_path)
    logging.info(f'Steps initial count: {df_steps.shape[0]}')
    df_topics = read_df(topics_path)
    logging.info(f'Topics initial size: {df_topics.shape[0]}')
    df_users = read_df(users_path)
    logging.info(f'Users initial size: {df_users.shape[0]}')

    # Filter submissions with more then max_attempts attempts
    df_submissions = df_submissions[df_submissions[SubmissionColumns.TOTAL_ATTEMPTS.value] <= max_attempts]
    logging.info(f'Select {df_submissions.shape[0]} submissions with <={max_attempts} attempts')

    # Filter steps which has header or footer
    df_steps = df_steps[df_steps[StepColumns.HAS_HEADER_FOOTER.value] == False]  # noqa: E712
    logging.info(f'Select {df_steps.shape[0]} steps with has_header_footer = False')

    # Filter submissions on steps with header or footer
    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID.value].isin(df_steps[StepColumns.ID])]
    logging.info(f'Select {df_submissions.shape[0]} submissions with has_header_footer = False')

    df_steps = df_steps[df_steps[StepColumns.ID.value].isin(df_submissions[SubmissionColumns.STEP_ID.value])]
    logging.info(f'Select {df_steps.shape[0]} steps which presented in submissions dataset')

    df_topics = df_topics[df_topics[TopicColumns.ID.value].isin(df_steps[StepColumns.TOPIC.value])]
    logging.info(f'Select {df_topics.shape[0]} topics which presented in submissions dataset')

    df_users = df_users[df_users[UserColumns.ID.value].isin(df_submissions[SubmissionColumns.USER_ID.value])]
    logging.info(f'Select {df_users.shape[0]} users which presented in submissions dataset')

    save_to_directory(df_submissions, submissions_path, result_directory_path)
    logging.info(f'Submissions final count: {df_submissions.shape[0]}')
    save_to_directory(df_steps, steps_path, result_directory_path)
    logging.info(f'Steps final count: {df_steps.shape[0]}')
    save_to_directory(df_topics, topics_path, result_directory_path)
    logging.info(f'Topics final count: {df_topics.shape[0]}')
    save_to_directory(df_users, users_path, result_directory_path)
    logging.info(f'Users final count: {df_users.shape[0]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('client_stats_path', type=str, help='Path to .csv file with client statistics.')
    parser.add_argument('submissions_stats_path', type=str, help='Path to .csv file with submissions stats.')
    parser.add_argument('issues_stats_path', type=str, help='Path to .csv file with issues stats.')

    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('users_path', type=str, help='Path to .csv file with users.')
    parser.add_argument('result_directory_path', type=str, help='Path to directory where to put resulted dataset')

    parser.add_argument('--max-attempts', '-db', type=int, default=5,
                        help='Maximum number of attempts to leave in dataset '
                             '(submissions with many attempts considered as noise).')

    args = parser.parse_args(sys.argv[1:])
    filter_dataset(args.submissions_path,
                   args.steps_path,
                   args.topics_path,
                   args.users_path,
                   args.result_directory_path,
                   args.max_attempts)
