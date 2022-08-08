import logging

import argparse
import sys
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.file_utils import create_file
from analysis.src.python.utils.logging_utils import configure_logger


def save_submission_series_to_files(submission_series: pd.DataFrame, submission_series_path: str):
    for i, submission in submission_series.iterrows():
        lang = submission[SubmissionColumns.LANG.value]
        extension = get_language_version(lang).extension_by_language()
        attempt = submission[SubmissionColumns.ATTEMPT.value]
        total_attempts = submission[SubmissionColumns.ATTEMPT.value]
        submission_id = submission[SubmissionColumns.ID.value]
        step_id = submission[SubmissionColumns.STEP_ID.value]
        code = submission[SubmissionColumns.CODE.value]

        file_name = f'code_{attempt}_{submission_id}{extension}'
        file_path = Path(submission_series_path) / f'step_{step_id}_{total_attempts}'
        next(create_file(file_path / file_name, content=code))


def main(submission_path: str, submission_series_path: str, total_attempts: int, count: int):
    df_submission = read_df(submission_path)
    df_submission_with_attempts = df_submission[df_submission[SubmissionColumns.TOTAL_ATTEMPTS.value] == total_attempts]
    df_submission_with_attempts \
        .groupby([SubmissionColumns.USER_ID.value, SubmissionColumns.STEP_ID.value]) \
        .apply(save_submission_series_to_files, submission_series_path=submission_series_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submission_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('submission_series_path', type=str, help='Path to .csv file with steps')
    parser.add_argument('--total-attempts', type=int, help='Issue example to search for')
    parser.add_argument('--count', type=int, default=1, help='Step to search templates for')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    # configure_logger(args.output_dir, 'search', args.log_path)

    main(args.submission_path,
         args.submission_series_path,
         args.total_attempts,
         args.count)
