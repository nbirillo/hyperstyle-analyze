import argparse
import logging
import sys
import time
import traceback

import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluation_args import configure_arguments
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.evaluation.utils.args_util import script_structure_rule
from analysis.src.python.evaluation.utils.pandas_util import get_language_version
from analysis.src.python.utils.df_utils import read_df, write_df
from analysis.src.python.utils.file_utils import create_file, get_output_path, remove_directory

logger = logging.getLogger(__name__)

HYPERSTYLE_TRACEBACK = 'hyperstyle_traceback'


def inspect_solution(df_solution: pd.DataFrame,
                     config: HyperstyleEvaluationConfig):
    solution_id = df_solution[SubmissionColumns.ID.value]
    code = df_solution[SubmissionColumns.CODE.value]
    language = df_solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(language)

    solution_dir_path = config.tmp_directory / f'solution_{solution_id}'
    solution_file_path = solution_dir_path / f'code{language_version.extension_by_language().value}'
    next(create_file(solution_file_path, code))

    command = config.build_command(solution_dir_path, language_version)
    results = run_in_subprocess(command)
    remove_directory(solution_dir_path)

    return results


def run_evaluation(df_solutions: pd.DataFrame, config: HyperstyleEvaluationConfig):
    df_solutions[HYPERSTYLE_TRACEBACK] = df_solutions.apply(inspect_solution, axis=1, config=config)
    return df_solutions


def main() -> int:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    try:
        start = time.time()
        args = parser.parse_args()
        df_solutions = read_df(args.solutions_file_path)
        config = HyperstyleEvaluationConfig(args)
        results = run_evaluation(df_solutions, config)
        write_df(results, get_output_path(args.solutions_file_path, '_hyperstyle'))
        end = time.time()
        print(f'All time: {end - start}')
        return 0

    except FileNotFoundError:
        logger.error('XLSX-file or CSV-file with the specified name does not exists.')
        return 2

    except KeyError:
        logger.error(script_structure_rule)
        return 2

    except Exception:
        traceback.print_exc()
        logger.exception('An unexpected error.')
        return 2


if __name__ == '__main__':
    sys.exit(main())
