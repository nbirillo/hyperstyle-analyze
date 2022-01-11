import argparse
import json
import logging
import sys

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.statistics_utils import get_statistics_by_group


def calculate_submissions_series_client_series(series: pd.DataFrame) -> pd.Series:
    """ For submissions series sort submissions by attempt number and build client series. """

    series = series.sort_values([SubmissionColumns.ATTEMPT])
    stats = {
        SubmissionColumns.GROUP: series[SubmissionColumns.GROUP].values[0],
        SubmissionColumns.CLIENT: json.dumps(list(series[SubmissionColumns.CLIENT].values)),
    }

    return pd.Series(stats)


def get_submissions_client_series(submissions_path: str,
                                  client_series_statistics_path: str,
                                  chunk_size: int):
    """ For each submissions series build client series (the sequence of clients). """

    df_submissions = pd.read_csv(submissions_path)

    min_group, max_group = df_submissions[SubmissionColumns.GROUP].min(), df_submissions[SubmissionColumns.GROUP].max()
    logging.info(f'Groups range: [{min_group}, {max_group}]')

    get_statistics_by_group(df_submissions, client_series_statistics_path, chunk_size,
                            calculate_submissions_series_client_series)


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with issues')
    parser.add_argument('client_series_statistics_path', type=str,
                        help='Path to .csv file with submissions client series statistics')
    parser.add_argument('--chunk-size', '-c', default=5000, type=int,
                        help='Number of groups which will be processed simultaneously')

    args = parser.parse_args(sys.argv[1:])
    get_submissions_client_series(args.submissions_path, args.client_series_statistics_path, args.chunk_size)
