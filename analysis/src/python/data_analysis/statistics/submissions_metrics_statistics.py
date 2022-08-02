import argparse
import sys

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.logging_utils import configure_logger
from analysis.src.python.data_analysis.utils.stats_utils import calculate_code_lines_count, \
    calculate_code_symbols_count, calculate_issues_count


def get_submission_statistics(submissions_with_issues_path: str, submissions_statistics_path: str):
    """ Calculate submissions metrics such number of code lines, symbols, issues. """

    df_submissions = read_df(submissions_with_issues_path)
    df_stats = df_submissions[[SubmissionColumns.ID.value]].copy()

    df_stats[SubmissionStatsColumns.CODE_LINES_COUNT.value] = df_submissions[SubmissionColumns.CODE.value] \
        .apply(calculate_code_lines_count)
    df_stats[SubmissionStatsColumns.CODE_SYMBOLS_COUNT.value] = df_submissions[SubmissionColumns.CODE.value] \
        .apply(calculate_code_symbols_count)

    df_stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_COUNT.value] = \
        df_submissions[SubmissionColumns.HYPERSTYLE_ISSUES.value].apply(calculate_issues_count)

    df_stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_BY_CODE_LINES.value] = \
        df_stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_COUNT.value] / \
        df_stats[SubmissionStatsColumns.CODE_LINES_COUNT.value]

    if SubmissionColumns.QODANA_ISSUES.value in df_submissions.columns:
        df_stats[SubmissionStatsColumns.QODANA_ISSUES_COUNT.value] = \
            df_submissions[SubmissionColumns.QODANA_ISSUES.value].apply(calculate_issues_count)

        df_stats[SubmissionStatsColumns.QODANA_ISSUES_BY_CODE_LINES.value] = \
            df_stats[SubmissionStatsColumns.QODANA_ISSUES_COUNT.value] / \
            df_stats[SubmissionStatsColumns.CODE_LINES_COUNT.value]

    write_df(df_stats, submissions_statistics_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('submissions_statistics_path', type=str,
                        help='Path to .csv file where to save submissions statistics')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.submissions_statistics_path, 'statistics', args.log_path)

    get_submission_statistics(args.submissions_path, args.submissions_statistics_path)
