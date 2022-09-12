import argparse
from functools import partial
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.utils.stats_utils import (
    calculate_code_lines_count,
    calculate_code_symbols_count,
    calculate_issues_count,
)
from analysis.src.python.utils.df_utils import read_df, write_df


def get_submission_statistics(
        submissions: pd.DataFrame,
        code_lines_count: bool = False,
        code_symbols_count: bool = False,
        hyperstyle_issue_count: bool = False,
        hyperstyle_issue_by_code_lines: bool = False,
        qodana_issue_count: bool = False,
        qodana_issue_by_code_lines: bool = False,
        ignore_empty_lines: bool = False,
) -> pd.DataFrame:
    """Calculate submissions metrics such number of code lines, symbols, issues."""

    stats = submissions[[SubmissionColumns.ID.value]].copy()

    if code_lines_count or hyperstyle_issue_by_code_lines or qodana_issue_by_code_lines:
        stats[SubmissionStatsColumns.CODE_LINES_COUNT.value] = submissions[SubmissionColumns.CODE.value].apply(
            partial(calculate_code_lines_count, ignore_empty_lines=ignore_empty_lines))

    if code_symbols_count:
        stats[SubmissionStatsColumns.CODE_SYMBOLS_COUNT.value] = submissions[SubmissionColumns.CODE.value].apply(
            calculate_code_symbols_count,
        )

    if hyperstyle_issue_count or hyperstyle_issue_by_code_lines:
        stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_COUNT.value] = submissions[
            SubmissionColumns.HYPERSTYLE_ISSUES.value
        ].apply(calculate_issues_count, issues_column=SubmissionColumns.HYPERSTYLE_ISSUES.value)

    if hyperstyle_issue_by_code_lines:
        stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_BY_CODE_LINES.value] = (
                stats[SubmissionStatsColumns.HYPERSTYLE_ISSUES_COUNT.value]
                / stats[SubmissionStatsColumns.CODE_LINES_COUNT.value]
        )

    if qodana_issue_count or qodana_issue_by_code_lines:
        stats[SubmissionStatsColumns.QODANA_ISSUE_COUNT.value] = submissions[
            SubmissionColumns.QODANA_ISSUES.value
        ].apply(calculate_issues_count, issues_column=SubmissionColumns.QODANA_ISSUES.value)

    if qodana_issue_by_code_lines:
        stats[SubmissionStatsColumns.QODANA_ISSUE_BY_CODE_LINES.value] = (
                stats[SubmissionStatsColumns.QODANA_ISSUE_COUNT.value]
                / stats[SubmissionStatsColumns.CODE_LINES_COUNT.value]
        )

    return stats


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions',
    )

    parser.add_argument(
        'submissions_statistics_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file where to save submissions statistics',
    )

    parser.add_argument(
        '--code-lines-count',
        action='store_true',
        help="Count the number of lines of code.",
    )

    parser.add_argument(
        '--code-symbols-count',
        action='store_true',
        help='Count the number of symbols in the code.',
    )

    parser.add_argument(
        '--hyperstyle-issue-count',
        action='store_true',
        help='Count the number of hyperstyle issues.',
    )

    parser.add_argument(
        '--hyperstyle-issue-by-code-lines',
        action='store_true',
        help='Calculate the frequency of hyperstyle issues.',
    )

    parser.add_argument(
        '--qodana-issue-count',
        action='store_true',
        help='Count the number of Qodana issues.',
    )

    parser.add_argument(
        '--qodana-issue-by-code-lines',
        action='store_true',
        help='Calculate the frequency of Qodana issues.',
    )

    parser.add_argument(
        '--ignore-empty-lines',
        action='store_true',
        help='Ignore empty lines during metrics count.',
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    submissions = read_df(args.submissions_path)

    submissions_with_stats = get_submission_statistics(
        submissions,
        args.code_lines_count,
        args.code_symbols_count,
        args.hyperstyle_issue_count,
        args.hyperstyle_issue_by_code_lines,
        args.qodana_issue_count,
        args.qodana_issue_by_code_lines,
        args.ignore_empty_lines,
    )

    write_df(submissions_with_stats, args.submissions_statistics_path)


if __name__ == '__main__':
    main()
