import argparse
import sys
import uuid
from pathlib import Path
from typing import List

import pandas as pd
from analysis.src.python.evaluation.model.column_name import ColumnName
from analysis.src.python.evaluation.utils.pandas_util import logger
from analysis.src.python.evaluation.utils.args_util import EvaluationRunToolArgument
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import get_parent_folder
from analysis.src.python.utils.extension_utils import AnalysisExtension

'''
This scripts allows unpacking solutions to the solutions dataframe.
The initial dataframe has only several obligatory columns user_id,times,codes,
where <times> is an array with times separated by ; symbol and
<codes> is an array with code fragments separated by ₣ symbol.
The <times> and <codes> arrays have to has the same length.
The resulting dataset will have several: columns user_id,time,code,
where each row contains obly one time and one code fragment
'''


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help='Path to the compressed solutions')


def __parse_time_and_solutions(times_str: str, solutions_str: str) -> pd.DataFrame:
    times = times_str.split(',')
    solutions = solutions_str.split('₣')
    time_to_solution = dict(zip(times, solutions))
    user_df = pd.DataFrame(time_to_solution.items(), columns=[ColumnName.TIME.value, ColumnName.CODE.value])
    user_df[ColumnName.USER.value] = uuid.uuid4()
    return user_df


def __add_user_df(user_df_list: List[pd.DataFrame], user_df: pd.DataFrame):
    user_df_list.append(user_df)


def main() -> int:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    try:
        args = parser.parse_args()
        solutions_file_path = args.solutions_file_path
        solutions_df = read_df(solutions_file_path)
        user_df_list = []
        solutions_df.apply(lambda row: __add_user_df(user_df_list,
                                                     __parse_time_and_solutions(row['times'], row['codes'])), axis=1)
        unpacked_solutions = pd.concat(user_df_list)
        output_path = get_parent_folder(Path(solutions_file_path)) / f'unpacked_solutions{AnalysisExtension.CSV.value}'
        write_df(unpacked_solutions, output_path)
        return 0

    except FileNotFoundError:
        logger.error('CSV-file with the specified name does not exists.')
        return 2

    except Exception:
        logger.exception('An unexpected error.')
        return 2


if __name__ == '__main__':
    sys.exit(main())
