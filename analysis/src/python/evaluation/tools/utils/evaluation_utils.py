import logging
import time
from pathlib import Path
from typing import Callable, List, TypeVar

import pandas as pd
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.tools.model.evaluation_config import EvaluationConfig
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.evaluation.tools.utils.saving_utils import save_solutions_to_files
from analysis.src.python.utils.df_utils import merge_dfs
from analysis.src.python.utils.file_utils import create_directory, remove_directory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_by_language(df_solutions: pd.DataFrame,
                         config: EvaluationConfig,
                         parse_result: Callable[[Path], pd.DataFrame]) -> pd.DataFrame:
    """
    Group solutions by language and run evaluation tool on groups of solutions with same language.
    Return solutions with evaluation results.
    """

    results = []

    for _, df_lang_solutions in df_solutions.groupby(SubmissionColumns.LANG.value):
        result = evaluate(df_lang_solutions, config, parse_result)
        results.append(result)

    df_results = pd.concat(results)
    df_solutions = merge_dfs(df_solutions, df_results,
                             left_on=SubmissionColumns.ID.value,
                             right_on=SubmissionColumns.ID.value,
                             how='left',
                             )
    return df_solutions


def evaluate_by_solution(df_solutions: pd.DataFrame,
                         config: EvaluationConfig,
                         parse_result: Callable[[Path], pd.Series]) -> pd.DataFrame:
    """
    Run evaluation tool on each solution separately.
    Return solutions with evaluation results.
    """

    results = df_solutions.apply(lambda solution: evaluate(solution.to_frame().T, config, parse_result), axis=1)

    return pd.concat([df_solutions, pd.DataFrame.from_records(results)], axis=1)


T = TypeVar('T')


def evaluate(df_solutions: pd.DataFrame, config: EvaluationConfig, parse_result: [[Path], T]) -> T:
    """
    Run tool on directory with group of solutions written on same language version.
    Return path to evaluation result.
    """

    language_versions = df_solutions[SubmissionColumns.LANG.value].apply(get_language_version).unique()
    assert language_versions.size == 1, "Given solution should have same language version"
    language_version = language_versions[0]

    language_version_path = create_directory(config.tmp_path / language_version.value, clear=True)
    input_path = create_directory(language_version_path / 'input', clear=True)
    output_path = create_directory(language_version_path / 'output', clear=True)

    save_solutions_to_files(df_solutions, language_version, input_path, config.with_template)

    command = config.build_command(input_path, output_path, language_version)
    evaluate_command(command)

    result = parse_result(output_path / config.result_path)

    remove_directory(language_version_path)

    return result


def evaluate_command(command: List[str]):
    logger.info('Start evaluation')
    start = time.time()

    logger.info('Executing command: ' + (' '.join(command)))
    run_in_subprocess(command)

    end = time.time()
    logger.info(f'Finish evaluation time={end - start}s')
