import argparse
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Set

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns, SubmissionStatsColumns
from analysis.src.python.data_analysis.utils.stats_utils import (
    calculate_code_lines_count,
    calculate_code_symbols_count,
    calculate_issues_count,
)
from analysis.src.python.utils.df_utils import read_df, write_df


class CodeLinesCountOption(Enum):
    ALL = 'all'
    IGNORE_EMPTY_LINES = 'ignore_empty_lines'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.ALL.value, cls.IGNORE_EMPTY_LINES.value}


def get_submission_statistics(
    submissions: pd.DataFrame,
    code_lines_count: Optional[CodeLinesCountOption] = None,
    code_symbols_count: bool = False,
    raw_issue_count: bool = False,
    raw_issue_by_code_lines: bool = False,
    qodana_issue_count: bool = False,
    qodana_issue_by_code_lines: bool = False,
) -> pd.DataFrame:
    """Calculate submissions metrics such number of code lines, symbols, issues."""

    stats = submissions[[SubmissionColumns.ID.value]].copy()

    if code_lines_count is not None:
        stats[SubmissionStatsColumns.CODE_LINES_COUNT.value] = submissions[SubmissionColumns.CODE.value].apply(
            partial(calculate_code_lines_count, ignore_empty_lines=True)
            if code_lines_count == CodeLinesCountOption.IGNORE_EMPTY_LINES
            else calculate_code_lines_count,
        )

    if code_symbols_count:
        stats[SubmissionStatsColumns.CODE_SYMBOLS_COUNT.value] = submissions[SubmissionColumns.CODE.value].apply(
            calculate_code_symbols_count,
        )

    if raw_issue_count:
        stats[SubmissionStatsColumns.RAW_ISSUE_COUNT.value] = submissions[SubmissionColumns.RAW_ISSUES.value].apply(
            calculate_issues_count,
        )

    if raw_issue_by_code_lines:
        stats[SubmissionStatsColumns.RAW_ISSUE_BY_CODE_LINES.value] = (
            stats[SubmissionStatsColumns.RAW_ISSUE_COUNT.value] / stats[SubmissionStatsColumns.CODE_LINES_COUNT.value]
        )

    if qodana_issue_count:
        stats[SubmissionStatsColumns.QODANA_ISSUE_COUNT.value] = submissions[
            SubmissionColumns.QODANA_ISSUES.value
        ].apply(calculate_issues_count)

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
        type=str,
        nargs='?',
        const=CodeLinesCountOption.ALL.value,
        choices=CodeLinesCountOption.values(),
        help="Count the number of lines of code. Select 'ignore_empty_lines' to ignore empty lines.",
    )

    parser.add_argument(
        '--code-symbols-count',
        type=bool,
        help='Count the number of symbols in the code.',
    )

    parser.add_argument(
        '--raw-issue-count',
        type=bool,
        help='Count the number of raw issues.',
    )

    parser.add_argument(
        '--raw-issue-by-code-lines',
        type=str,
        help='Calculate the frequency of raw issues.',
    )

    parser.add_argument(
        '--qodana-issue-count',
        type=bool,
        help='Count the number of Qodana issues.',
    )

    parser.add_argument(
        '--qodana-issue-by-code-lines',
        type=bool,
        help='Calculate the frequency of Qodana issues.',
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    if args.code_lines_count is not None:
        args.code_lines_count = CodeLinesCountOption(args.code_lines_count)

    submissions = read_df(args.submissions_path)

    submissions_with_stats = get_submission_statistics(
        submissions,
        args.code_lines_count,
        args.code_symbols_count,
        args.raw_issue_count,
        args.raw_issue_by_code_lines,
        args.qodana_issue_count,
        args.qodana_issue_by_code_lines,
    )

    write_df(submissions_with_stats, args.submissions_statistics_path)


if __name__ == '__main__':
    main()
