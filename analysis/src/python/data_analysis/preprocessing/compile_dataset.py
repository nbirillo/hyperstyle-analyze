import argparse
import logging
import sys

from analysis.src.python.data_analysis.model.column_name import StepColumns, SubmissionColumns, TopicColumns, \
    UserColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.data_analysis.utils.logging_utlis import configure_logger


def filter_dataset(submissions_path: str, steps_path: str, topics_path: str, users_path: str):
    """ Create directory with result dataset to analyse. Filter submissions with more then `max_attempts`. """

    df_submissions = read_df(submissions_path)
    logging.info(f'Submissions initial count: {df_submissions.shape[0]}')
    df_steps = read_df(steps_path)
    logging.info(f'Steps initial count: {df_steps.shape[0]}')
    df_topics = read_df(topics_path)
    logging.info(f'Topics initial size: {df_topics.shape[0]}')
    df_users = read_df(users_path)
    logging.info(f'Users initial size: {df_users.shape[0]}')

    # Filter submissions on steps with header or footer
    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID].isin(df_steps[StepColumns.ID])]
    logging.info(f'Select {df_submissions.shape[0]} submissions with has_header_footer = False')

    df_steps = df_steps[df_steps[StepColumns.ID].isin(df_submissions[SubmissionColumns.STEP_ID])]
    logging.info(f'Select {df_steps.shape[0]} steps which presented in submissions dataset')

    df_topics = df_topics[df_topics[TopicColumns.ID].isin(df_steps[StepColumns.TOPIC])]
    logging.info(f'Select {df_topics.shape[0]} topics which presented in submissions dataset')

    df_users = df_users[df_users[UserColumns.ID].isin(df_submissions[SubmissionColumns.USER_ID])]
    logging.info(f'Select {df_users.shape[0]} users which presented in submissions dataset')

    write_df(df_submissions, submissions_path)
    logging.info(f'Submissions final count: {df_submissions.shape[0]}')
    write_df(df_steps, steps_path)
    logging.info(f'Steps final count: {df_steps.shape[0]}')
    write_df(df_topics, topics_path)
    logging.info(f'Topics final count: {df_topics.shape[0]}')
    write_df(df_users, users_path)
    logging.info(f'Users final count: {df_users.shape[0]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('users_path', type=str, help='Path to .csv file with users.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.submissions_path, 'compile')

    filter_dataset(args.submissions_path,
                   args.steps_path,
                   args.topics_path,
                   args.users_path)
