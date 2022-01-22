import argparse
import json
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import Client, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, parallel_apply, read_df, rename_columns, \
    write_df
from analysis.src.python.data_analysis.utils.parsing_utils import parse_qodana_issues


def merge_submissions_with_issues(df_submissions: pd.Dataframe, df_issues: pd.Dataframe, issue_columns: str):
    """ Merges submissions with issues. """

    df_issues = df_issues[[SubmissionColumns.ID, SubmissionColumns.RAW_ISSUES, SubmissionColumns.CODE]]
    df_submissions = merge_dfs(df_submissions, df_issues, SubmissionColumns.CODE, SubmissionColumns.CODE, how='left')
    df_submissions[issue_columns] = df_submissions[issue_columns].fillna(value=json.dumps([]))
    return df_submissions


def get_client_tag(base_client: str):
    """ Get client tag (idea is universal tag of all ides). """

    if base_client == Client.WEB.value:
        return Client.WEB.value
    return Client.IDEA.value


def build_submissions_dataframe(submissions_path: str,
                                submissions_to_users_path: str,
                                raw_issues_path: str,
                                qodana_issues_path: str,
                                submissions_with_issues_path: str):
    """ Merges submissions dataset with users information and issues. """

    logging.info(f'Reading submissions from: {submissions_path}')
    df_submissions = read_df(submissions_path)
    logging.info(f'Finish readings submissions dataframe [shape: {df_submissions.shape}]')

    if submissions_to_users_path is not None:
        logging.info(f'Reading submissions to users from: {submissions_to_users_path}')
        df_submissions_to_users = read_df(submissions_to_users_path)
        logging.info(f'Finish readings submissions to users dataframe [shape: {df_submissions_to_users.shape}]')

        logging.info('Merging submissions with submissions to users')
        df_submissions = merge_dfs(df_submissions, df_submissions_to_users, SubmissionColumns.ID, SubmissionColumns.ID)
        logging.info(f'Finish merging submissions with submissions to users [shape: {df_submissions.shape}]')

    logging.info(f'Reading raw issues from: {raw_issues_path}')
    df_raw_issues = read_df(raw_issues_path)
    logging.info(f'Finish readings raw issues dataframe [shape: {df_raw_issues.shape}]')

    logging.info('Merging submissions with raw issues')
    df_submissions = merge_submissions_with_issues(df_submissions, df_raw_issues, SubmissionColumns.RAW_ISSUES)
    logging.info(f'Finish merging submissions with raw issues [shape: {df_submissions.shape}]')

    logging.info(f'Reading qodana issues from: {qodana_issues_path}')
    df_qodana_issues = read_df(qodana_issues_path)
    logging.info(f'Finish readings qodana issues dataframe [shape: {df_qodana_issues.shape}]')

    logging.info('Preprocessing qodana issues')
    df_qodana_issues = rename_columns(df_qodana_issues, columns={'inspections': SubmissionColumns.QODANA_ISSUES})
    df_qodana_issues = parallel_apply(df_qodana_issues, SubmissionColumns.QODANA_ISSUES, parse_qodana_issues)

    logging.info('Merging submissions with qodana issues')
    df_submissions = merge_submissions_with_issues(df_submissions, df_qodana_issues, SubmissionColumns.QODANA_ISSUES)
    logging.info(f'Finish merging submissions with qodana issues [shape: {df_submissions.shape}]')

    df_submissions[SubmissionColumns.BASE_CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value]
    df_submissions[SubmissionColumns.CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value] \
        .apply(get_client_tag)

    write_df(df_submissions, submissions_with_issues_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to file with submissions')
    parser.add_argument('raw_issues_path', type=str, help='Path to file with raw issues/submission relation.')
    parser.add_argument('qodana_issues_path', type=str, help='Path to file with qodana issues/submission relation.')
    parser.add_argument('preprocessed_submissions_path', type=str,
                        help='Path to output file with submissions with issues.')
    parser.add_argument('--users-to-submissions-path', type=str, default=None,
                        help='Path to file with user/submission relation '
                             '(if data is not presented in submissions dataset or was anonymize).')

    args = parser.parse_args(sys.argv[1:])

    build_submissions_dataframe(args.submissions_path,
                                args.users_to_submissions_path,
                                args.raw_issues_path,
                                args.qodana_issues_path,
                                args.preprocessed_submissions_path)
