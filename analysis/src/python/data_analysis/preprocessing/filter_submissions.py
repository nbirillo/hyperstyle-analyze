import logging
from enum import Enum, unique

import numpy as np
import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.parsing_utils import str_to_datetime


def check_same_code(submission_0: pd.Series, submission_1: pd.Series) -> bool:
    """ Check if submission not the same as previous. """

    return submission_0[SubmissionColumns.CODE].strip() == submission_1[SubmissionColumns.CODE].strip()


def check_different_code(submission_0: pd.Series, submission_1: pd.Series, diff_ratio: float) -> bool:
    """ Check if submission not so different with previous (lines number does not changed in `diff_ratio` times). """

    code_0 = submission_0[SubmissionColumns.CODE]
    code_1 = submission_1[SubmissionColumns.CODE]
    code_lines_diff = len(code_0) / len(code_1)
    return not (1 / diff_ratio <= code_lines_diff <= diff_ratio)


@unique
class SubmissionsCheckStatus(Enum):
    OK = 'ok'
    SAME = 'same'
    DIFFERENT = 'different'


def filter_submissions_series(submissions_series: pd.DataFrame, diff_ratio: float) -> pd.DataFrame:
    """ Filter submissions in submission series (group of submissions by one user on one step). """

    logging.info(f'Processing submission series group {submissions_series.iloc[0][SubmissionColumns.GROUP]}')
    logging.info(f'Initial group shape {submissions_series.shape}')

    status = []
    submissions_series[SubmissionColumns.TIME] = submissions_series[SubmissionColumns.TIME].apply(str_to_datetime)
    submissions_series.sort_values([SubmissionColumns.TIME], inplace=True)

    prev_submission = None
    attempt = 0
    for i, submission in submissions_series.iterrows():
        attempt += 1

        if prev_submission is not None:
            if check_same_code(prev_submission, submission):
                logging.info(f'Drop submission: '
                             f'user={submission[SubmissionColumns.USER_ID]} '
                             f'step={submission[SubmissionColumns.STEP_ID]} '
                             f'attempt={attempt + 1}: '
                             f'same submissions')
                status.append(SubmissionsCheckStatus.SAME)
                continue
            elif check_different_code(submission, submission, diff_ratio):
                logging.info(f'Drop submission: '
                             f'user={submission[SubmissionColumns.USER_ID]} '
                             f'step={submission[SubmissionColumns.STEP_ID]} '
                             f'attempt={attempt + 1}: '
                             f'different submissions')
                status.append(SubmissionsCheckStatus.DIFFERENT)
                continue

        prev_submission = submission
        status.append(SubmissionsCheckStatus.OK)

    submissions_series = submissions_series[np.array(status) == SubmissionsCheckStatus.OK].copy()
    group_size = submissions_series.shape[0]
    submissions_series[SubmissionColumns.ATTEMPT] = list(range(1, group_size + 1))
    submissions_series[SubmissionColumns.TOTAL_ATTEMPTS] = [group_size] * group_size

    logging.info(f'Final group shape {submissions_series.shape}')

    return submissions_series


def filter_submissions_without_code(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Filter submissions with integer answer instead of code string. """

    df_submissions = df_submissions[df_submissions[SubmissionColumns.CODE].apply(lambda x: isinstance(x, str))]
    logging.info('Filter submissions without code (test cases or other)')

    return df_submissions


def filter_submissions_with_many_attempts(df_submissions: pd.DataFrame, max_attempts: int) -> pd.DataFrame:
    """ Filter submissions with more then max attempts. """

    df_submissions = df_submissions[df_submissions[SubmissionColumns.TOTAL_ATTEMPTS] <= max_attempts]
    logging.info(f'Filter submissions with > {max_attempts} attempts. Submissions shape: {df_submissions.shape}')

    return df_submissions
