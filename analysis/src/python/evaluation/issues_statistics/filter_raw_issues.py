import argparse
import logging
from pathlib import Path

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.language import Language
from hyperstyle.src.python.review.reviewers.utils.issues_filter import filter_low_measure_issues

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.utils.df_utils import read_df, rename_columns, write_df
from analysis.src.python.utils.file_utils import get_output_path
from analysis.src.python.utils.parsing_utils import dump_raw_issues_to_str, parse_raw_issues_to_objects


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('solutions_file_path',
                        type=lambda value: Path(value).absolute(),
                        help="File in csv or xlsx format with solution and detected raw issues",
                        )


def _filter_issues_in_solution(df_solution: pd.DataFrame) -> str:
    issues_str = df_solution[SubmissionColumns.RAW_ISSUES_ALL.value]
    issues = parse_raw_issues_to_objects(issues_str)

    lang = df_solution[SubmissionColumns.LANG.value]
    language_version = LanguageVersion.from_value(lang)
    language = Language.from_language_version(language_version)

    logging.info(f'Issues before filtering {len(issues)}')
    issues = filter_low_measure_issues(issues, language)
    logging.info(f'Issues after filtering {len(issues)}')

    return dump_raw_issues_to_str(issues)


def _get_issues_diff(df_solution: pd.DataFrame) -> str:
    issues_all_str = df_solution[SubmissionColumns.RAW_ISSUES_ALL.value]
    issues_all = parse_raw_issues_to_objects(issues_all_str)

    issues_str = df_solution[SubmissionColumns.RAW_ISSUES.value]
    issues = parse_raw_issues_to_objects(issues_str)

    issues_diff = [issue for issue in issues_all if issue not in issues]

    return dump_raw_issues_to_str(issues_diff)


def filter_raw_issues(df_solutions: pd.DataFrame):
    df_solutions = rename_columns(df_solutions,
                                  {SubmissionColumns.RAW_ISSUES.value: SubmissionColumns.RAW_ISSUES_ALL.value})
    df_solutions[SubmissionColumns.RAW_ISSUES.value] = df_solutions.apply(_filter_issues_in_solution, axis=1)
    df_solutions[SubmissionColumns.RAW_ISSUES_DIFF.value] = df_solutions.apply(_get_issues_diff, axis=1)
    return df_solutions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    solutions_df = read_df(args.solutions_file_path)
    output_df = filter_raw_issues(solutions_df)
    output_file_path = get_output_path(args.solutions_file_path, '_filtered')
    write_df(output_df, output_file_path)
