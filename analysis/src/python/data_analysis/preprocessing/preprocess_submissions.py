import argparse
import sys

from analysis.src.python.data_analysis.model.column_name import Client, SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df, write_df


def get_client_tag(base_client: str):
    if base_client == Client.WEB.value:
        return Client.WEB.value
    return Client.IDEA.value


def preprocess_submissions(submissions_path: str):
    df_submissions = read_df(submissions_path)
    df_submissions[SubmissionColumns.BASE_CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value]
    df_submissions[SubmissionColumns.CLIENT.value] = df_submissions[SubmissionColumns.CLIENT.value] \
        .apply(get_client_tag)
    write_df(df_submissions, submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')

    args = parser.parse_args(sys.argv[1:])
    preprocess_submissions(args.submissions_path)
