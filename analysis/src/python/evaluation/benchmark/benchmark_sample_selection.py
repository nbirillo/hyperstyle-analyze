import argparse
from pathlib import Path
from typing import List, Optional

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.utils.stats_utils import calculate_code_lines_count
from analysis.src.python.utils.df_utils import read_df, write_df


def get_sample(df_submissions: pd.DataFrame,
               sample_size: int,
               step_ids: Optional[List[int]],
               line_counts: Optional[List[int]],
               random_state: Optional[int] = 42) -> pd.DataFrame:
    if step_ids is not None:
        df_submissions = df_submissions[df_submissions[SubmissionColumns.STEP_ID.value].isin(step_ids)]

    df_samples = []

    if line_counts is not None:
        df_submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value] = \
            df_submissions[SubmissionColumns.CODE.value].apply(calculate_code_lines_count)

        for i in range(1, len(line_counts)):
            left_border = line_counts[i - 1]
            right_border = line_counts[i]
            df_sample = df_submissions[(df_submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value] > left_border) & (
                    df_submissions[SubmissionStatsColumns.CODE_LINES_COUNT.value] <= right_border)]
            df_samples.append(df_sample.sample(sample_size, random_state=random_state, replace=True))

    if len(df_samples) == 0:
        df_samples.append(df_submissions.sample(sample_size, random_state=random_state, replace=True))

    return pd.concat(df_samples)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file with submissions.')

    parser.add_argument('output_path', type=lambda value: Path(value).absolute(),
                        help='Path to .csv file where to save sample submissions.')

    parser.add_argument('--sample-size', type=int, default=10,
                        help='Number of submissions for each configuration.')

    parser.add_argument('--step-ids', type=int, nargs='+', default=None,
                        help='Step ids to get sample from.')

    parser.add_argument('--line-counts', type=int, nargs='+', default=None,
                        help='Line counts to get sample from.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    df_submissions = read_df(args.submissions_path)

    df_sample = get_sample(df_submissions, args.sample_size, args.step_ids, args.line_counts)
    write_df(df_sample, args.output_path)
