import argparse
import json
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import append_df, write_df


def calculate_submissions_series_client_series(series: pd.DataFrame) -> pd.Series:
    """ For submissions series sort submissions by attempt number and build client series. """

    series = series.sort_values([SubmissionColumns.ATTEMPT])
    stats = {
        SubmissionColumns.GROUP: series[SubmissionColumns.GROUP].values[0],
        SubmissionColumns.CLIENT: json.dumps(list(series[SubmissionColumns.CLIENT].values)),
    }

    return pd.Series(stats)


def get_submissions_client_series(submissions_path: str,
                                  submissions_client_series_path: str,
                                  chunk_size: int):
    """ For each submissions series build client series (the sequence of clients). """

    df_submissions = pd.read_csv(submissions_path)

    min_group, max_group = df_submissions[SubmissionColumns.GROUP].min(), df_submissions[SubmissionColumns.GROUP].max()
    logging.info(f'Groups range: [{min_group}, {max_group}]')

    for i in range(min_group, max_group + 1, chunk_size):
        min_group_index, max_group_index = i, i + chunk_size - 1
        logging.info(f'Processing groups: [{min_group_index}, {max_group_index})')

        df_groups_submission_series = df_submissions[
            df_submissions[SubmissionColumns.GROUP].between(min_group_index, max_group_index, inclusive=True)]
        logging.info('Finish selection')

        df_grouped_submission_series = df_groups_submission_series.groupby([SubmissionColumns.GROUP], as_index=False)
        logging.info('Finish grouping')

        df_client_series = df_grouped_submission_series.apply(calculate_submissions_series_client_series)
        logging.info('Finish filtering')

        df_client_series = df_client_series.reset_index(drop=True)
        logging.info('Finish aggregation')
        if i == 0:
            write_df(df_client_series, submissions_client_series_path)
        else:
            append_df(df_client_series, submissions_client_series_path)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with issues')
    parser.add_argument('submissions_client_series_path', type=str,
                        help='Path to .csv file with submissions client series statistics')
    parser.add_argument('--chunk-size', '-c', default=5000, type=int,
                        help='Number of groups which will be processed simultaneously')

    args = parser.parse_args(sys.argv[1:])
    get_submissions_client_series(args.submissions_path, args.submissions_client_series_path, args.chunk_size)
