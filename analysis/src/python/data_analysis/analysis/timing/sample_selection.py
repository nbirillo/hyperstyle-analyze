import argparse
import sys
from typing import List

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df


def get_random_submission_with_lines_count(submissions_stats_path: str, lines_counts: List[int]) -> List[int]:
    df_submissions_stats = read_df(submissions_stats_path)

    submission_ids = []
    for lines_count in lines_counts:
        submission_stats = \
            df_submissions_stats[df_submissions_stats[SubmissionStatsColumns.CODE_LINES_COUNT] == lines_count].sample()
        submission_ids.append(submission_stats[SubmissionColumns.ID].values[0])

    return submission_ids


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_stats_path', type=str,
                        help='Path to .csv file with preprocessed submissions stats')
    parser.add_argument('--lines-counts', nargs='+', type=int,
                        help='Lines counts of submissions to evaluate code quality analyzers time')

    args = parser.parse_args(sys.argv[1:])
    submission_ids = get_random_submission_with_lines_count(args.submissions_stats_path, args.lines_counts)

    print(*submission_ids)
