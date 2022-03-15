import argparse
import sys
from typing import List

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.utils.df_utils import merge_dfs, read_df, write_df


def get_random_submission_with_lines_count(submissions_path: str,
                                           submissions_stats_path: str,
                                           lines_counts: List[int],
                                           n_samples: int,
                                           selected_submissions_path: str):
    """Select random `n_samples` submissions with `lines_counts` lines counts. """

    df_submissions = read_df(submissions_path)
    df_submissions_stats = read_df(submissions_stats_path)
    df_submissions_stats = merge_dfs(df_submissions, df_submissions_stats,
                                     left_on=SubmissionColumns.ID.value,
                                     right_on=SubmissionColumns.ID.value)

    df_selected_submissions = df_submissions_stats[
        df_submissions_stats[SubmissionStatsColumns.CODE_LINES_COUNT.value].isin(lines_counts)] \
        .groupby(SubmissionStatsColumns.CODE_LINES_COUNT.value) \
        .apply(lambda g: g.sample(n_samples)).reset_index(drop=True)

    write_df(df_selected_submissions, selected_submissions_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions')
    parser.add_argument('submissions_stats_path', type=str,
                        help='Path to .csv file with preprocessed submissions stats')
    parser.add_argument('selected_submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions stats')
    parser.add_argument('--lines-counts', nargs='+', type=int,
                        help='Lines counts of submissions to evaluate code quality analyzers time')
    parser.add_argument('--n-samples', type=int,
                        help='Number of submissions with each values of lies count')

    args = parser.parse_args(sys.argv[1:])

    get_random_submission_with_lines_count(args.submissions_path,
                                           args.submissions_stats_path,
                                           args.lines_counts,
                                           args.n_samples,
                                           args.selected_submissions_path)
