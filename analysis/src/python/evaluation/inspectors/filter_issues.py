import argparse
from pathlib import Path
from typing import List, Set

import pandas as pd
from hyperstyle.src.python.review.inspectors.issue import BaseIssue
from hyperstyle.src.python.review.quality.penalty import PenaltyIssue

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument, parse_set_arg
from analysis.src.python.evaluation.utils.pandas_utils import get_issues_from_json
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.utils.file_utils import get_parent_folder
from analysis.src.python.utils.serialization_utils import serialize_data_and_write_to_file

TRACEBACK = ColumnName.TRACEBACK.value
ID = ColumnName.ID.value
GRADE = ColumnName.GRADE.value


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description}'
                             f'\nAll code fragments from this file must be graded ')

    parser.add_argument('-i', '--issues',
                        help='Set of issues',
                        default='')


def __get_new_issues(traceback: str, new_issues_classes: Set[str]) -> List[PenaltyIssue]:
    all_issues = get_issues_from_json(traceback)
    return list(filter(lambda i: i.origin_class in new_issues_classes, all_issues))


def __add_issues_for_fragment(fragment_id: int, new_issues: List[BaseIssue], diffs: dict) -> None:
    if len(new_issues) > 0:
        diffs[TRACEBACK][fragment_id] = new_issues


# Make a dict with the same structure as in the find_diffs function from diffs_between_df.py
def get_statistics_dict(solutions_df: pd.DataFrame, new_issues_classes: Set[str]) -> dict:
    diffs = {
        GRADE: [],
        TRACEBACK: {},
    }
    solutions_df.apply(lambda row: __add_issues_for_fragment(row[ID],
                                                             __get_new_issues(row[TRACEBACK], new_issues_classes),
                                                             diffs), axis=1)
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    solutions_file_path = args.solutions_file_path
    solutions_df = read_df(solutions_file_path)
    issues = parse_set_arg(args.issues)

    diffs = get_statistics_dict(solutions_df, issues)
    output_path = get_parent_folder(Path(solutions_file_path)) / f'diffs{AnalysisExtension.PICKLE.value}'
    serialize_data_and_write_to_file(output_path, diffs)


if __name__ == '__main__':
    main()
