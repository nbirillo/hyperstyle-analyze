import argparse
import os
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import Client, StepColumns, SubmissionColumns, TopicColumns, \
    UserColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df
from analysis.src.python.evaluation.common.file_util import create_directory, get_name_from_path


def get_client_tag(base_client: str):
    """ Get client tag (idea is universal tag of all ides). """

    if base_client == Client.WEB.value:
        return Client.WEB.value
    return Client.IDEA.value


def save_to_directory(df: pd.DataFrame, path: str, directory_path: str):
    """ Save dataframe to new directory. """

    write_df(df, os.path.join(directory_path, get_name_from_path(path)))


def preprocess_submissions(submissions_path: str, steps_path: str, topics_path: str, users_path: str,
                           result_directory_path: str, max_attempts: int):
    """ Create directory with result dataset to analyse. Filter submissions with more then `max_attempts`. """

    df_submissions = read_df(submissions_path)
    df_submissions[SubmissionColumns.BASE_CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value]
    df_submissions[SubmissionColumns.CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value] \
        .apply(get_client_tag)

    df_steps = read_df(steps_path)
    df_topics = read_df(topics_path)
    df_users = read_df(users_path)

    # Select submissions with total_attempts <= 5
    df_submissions = df_submissions[df_submissions[SubmissionColumns.LANG] <= max_attempts]

    # Select steps with has_template = False
    df_steps = df_steps[df_steps[StepColumns.HAS_TEMPLATE] is False]
    # Select submissions for steps with has_template = False
    df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID].isin(df_steps[StepColumns.ID])]
    # Select steps which do present in dataset
    df_steps = df_steps[df_steps[StepColumns.ID].isin(df_submissions[SubmissionColumns.STEP_ID])]
    # Select topics which do present in dataset
    df_topics = df_topics[df_topics[TopicColumns.ID].isin(df_steps[StepColumns.TOPIC])]
    # Select users which do present in dataset
    df_users = df_users[df_users[UserColumns.ID].isin(df_submissions[SubmissionColumns.USER_ID])]

    create_directory(result_directory_path)
    save_to_directory(df_steps, steps_path, result_directory_path)
    save_to_directory(df_topics, topics_path, result_directory_path)
    save_to_directory(df_users, users_path, result_directory_path)
    save_to_directory(df_submissions, submissions_path, result_directory_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('topics_path', type=str, help='Path to .csv file with topics.')
    parser.add_argument('users_path', type=str, help='Path to .csv file with users.')
    parser.add_argument('result_directory_path', type=str, help='Path to directory where to put resulted dataset')

    parser.add_argument('--max-attempts', '-db', type=int, default=5,
                        help='Maximum number of attempts to leave in dataset '
                             '(submissions with many attempts considered as noise).')

    args = parser.parse_args(sys.argv[1:])
    preprocess_submissions(args.submissions_path,
                           args.steps_path,
                           args.topics_path,
                           args.users_path,
                           args.result_directory_path,
                           args.max_attempts)
