import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.utils.args_utils import EvaluationRunToolArgument
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.extension_utils import AnalysisExtension, get_restricted_extension
from analysis.src.python.utils.file_utils import get_parent_folder

CodeToGradesDict = Dict[str, Tuple[str, Optional[str]]]


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name}_all',
                        type=lambda value: Path(value).absolute(),
                        help=f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description}'
                             f'\nAll code fragments from this file must be in the uniq file')

    parser.add_argument(f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name}_uniq',
                        type=lambda value: Path(value).absolute(),
                        help=f'{EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description}'
                             f'\nAll code fragments from this file must be graded '
                             f'(file contains grade and traceback (optional) columns)')


def __add_grade(code_to_grades_dict: CodeToGradesDict, code: str, grade: str, traceback: Optional[str]) -> None:
    code_to_grades_dict[code] = (grade, traceback)


# Return a dictionary that contains code fragments
# with their grades and traceback (optional, can be None)
def get_code_to_grades_dict(df: pd.DataFrame) -> CodeToGradesDict:
    code_to_grades_dict: CodeToGradesDict = {}
    df.apply(lambda row: __add_grade(code_to_grades_dict,
                                     row[ColumnName.CODE.value],
                                     row[ColumnName.GRADE.value],
                                     row[ColumnName.TRACEBACK.value]), axis=1)
    return code_to_grades_dict


def fill_all_solutions_df(all_solutions_df: pd.DataFrame, code_to_grades_dict: CodeToGradesDict) -> pd.DataFrame:
    all_solutions_df[ColumnName.GRADE.value], all_solutions_df[ColumnName.TRACEBACK.value] = zip(
        *all_solutions_df[ColumnName.CODE.value].map(lambda code: code_to_grades_dict[code]))
    return all_solutions_df


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    all_solutions_file_path = args.solutions_file_path_all
    output_ext = get_restricted_extension(all_solutions_file_path, [AnalysisExtension.XLSX, AnalysisExtension.CSV])
    all_solutions_df = read_df(all_solutions_file_path)
    uniq_solutions_df = read_df(args.solutions_file_path_uniq)

    code_to_grades_dict = get_code_to_grades_dict(uniq_solutions_df)
    all_solutions_df = fill_all_solutions_df(all_solutions_df, code_to_grades_dict)

    output_path = get_parent_folder(Path(all_solutions_file_path))
    write_df(all_solutions_df, output_path / f'evaluation_result_all{output_ext.value}')


if __name__ == '__main__':
    main()
