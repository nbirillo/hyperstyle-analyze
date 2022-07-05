import argparse
import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.inspectors.issue import IssueType
from hyperstyle.src.python.review.quality.penalty import PenaltyIssue

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.paper_evaluation.user_dynamics.user_statistics import DynamicsColumn
from analysis.src.python.evaluation.utils.args_util import EvaluationRunToolArgument
from analysis.src.python.evaluation.utils.pandas_util import get_issues_from_json, logger
from analysis.src.python.utils.df_utils import filter_df_by_single_value, read_df, write_df
from analysis.src.python.utils.extension_utils import AnalysisExtension
from analysis.src.python.utils.file_utils import get_parent_folder


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value)


ALL_ISSUES_COUNT = DynamicsColumn.ALL_ISSUES_COUNT.value
FORMATTING_ISSUES_COUNT = DynamicsColumn.FORMATTING_ISSUES_COUNT.value
OTHER_ISSUES_COUNT = DynamicsColumn.OTHER_ISSUES_COUNT.value


def __get_all_issues(traceback: str) -> List[PenaltyIssue]:
    return list(filter(lambda i: i.type != IssueType.INFO, get_issues_from_json(traceback)))


def __get_formatting_issues(traceback: str) -> List[PenaltyIssue]:
    return list(filter(lambda i: i.type == IssueType.CODE_STYLE, __get_all_issues(traceback)))


def __write_dynamics(output_path: Path, user_fragments: pd.DataFrame, index: int) -> None:
    output_path.mkdir(parents=True, exist_ok=True)
    user_fragments.columns = [DynamicsColumn.ISSUE_COUNT.value]
    user_fragments[ColumnName.TIME.value] = np.arange(len(user_fragments))
    write_df(user_fragments, output_path / f'user_{index}{AnalysisExtension.CSV.value}')


def __get_users_statistics(solutions_df: pd.DataFrame, output_path: Path) -> None:
    users = solutions_df[ColumnName.USER.value].unique()
    for index, user in enumerate(users):
        user_df = filter_df_by_single_value(solutions_df,
                                            ColumnName.USER.value, user).sort_values(ColumnName.TIME.value)
        user_df[ALL_ISSUES_COUNT] = user_df.apply(lambda row:
                                                  len(__get_all_issues(
                                                      row[ColumnName.TRACEBACK.value])),
                                                  axis=1)
        user_df[FORMATTING_ISSUES_COUNT] = user_df.apply(lambda row:
                                                         len(__get_formatting_issues(
                                                             row[ColumnName.TRACEBACK.value])),
                                                         axis=1)
        user_df[OTHER_ISSUES_COUNT] = user_df[ALL_ISSUES_COUNT] - user_df[FORMATTING_ISSUES_COUNT]

        __write_dynamics(output_path / 'all', user_df[[ALL_ISSUES_COUNT]], index)
        __write_dynamics(output_path / 'formatting', user_df[[FORMATTING_ISSUES_COUNT]], index)
        __write_dynamics(output_path / 'other', user_df[[OTHER_ISSUES_COUNT]], index)


def main() -> int:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    try:
        args = parser.parse_args()
        solutions_file_path = args.solutions_file_path
        solutions_df = read_df(solutions_file_path)

        output_path = get_parent_folder(Path(solutions_file_path)) / 'dynamics'
        output_path.mkdir(parents=True, exist_ok=True)
        __get_users_statistics(solutions_df, output_path)
        return 0

    except FileNotFoundError:
        logger.error('CSV-file with the specified name does not exists.')
        return 2

    except Exception:
        logger.exception('An unexpected error.')
        return 2


if __name__ == '__main__':
    sys.exit(main())
