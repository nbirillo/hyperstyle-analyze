import argparse
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.evaluation_args import configure_arguments
from analysis.src.python.evaluation.qodana.evaluation_config import QodanaEvaluationConfig
from analysis.src.python.evaluation.qodana.model.report import QodanaReport
from analysis.src.python.evaluation.utils.evaluation_utils import run_evaluation_command
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.evaluation.utils.solutions_saving_utils import get_solution_id_by_file_path, \
    save_solutions_to_files
from analysis.src.python.utils.df_utils import dict_to_df, merge_dfs, read_df, write_df
from analysis.src.python.utils.file_utils import create_directory, get_output_filename, get_output_path, \
    remove_directory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

QODANA_OUTPUT_SUFFIX = '_qodana'


def evaluate_solutions(df_solutions: pd.DataFrame, lang: str, config: QodanaEvaluationConfig) -> pd.DataFrame:
    """ Run qodana tool on directory with group of solutions written on same language version. """

    language_version = get_language_version(lang)

    language_version_path = create_directory(config.tmp_directory / language_version.value)
    input_path = create_directory(language_version_path / 'input')
    output_path = create_directory(language_version_path / 'output')

    save_solutions_to_files(df_solutions, language_version, input_path, with_template=True)
    command = config.build_command(input_path, output_path, language_version)

    run_evaluation_command(command)
    result_path = config.get_result_path(output_path)

    result = parse_result(result_path)
    remove_directory(language_version_path)

    return result


def parse_result(result_path: Path) -> pd.DataFrame:
    """ Parse results for group of solution and split by solution id. """

    try:
        with open(result_path, 'r') as f:
            report = QodanaReport.from_str(f.read())
    except Exception as e:
        raise Exception(f"Can not parse new format report from qodana output", e)

    results_dict = defaultdict(list)

    for problem in report.list_problem:
        for source in problem.sources:
            solution_id = get_solution_id_by_file_path(source.path)
            results_dict[solution_id].append(problem)

    results_dict = {i: QodanaReport(report.version, problems).to_str()
                    for i, problems in results_dict.items()}

    df_results = dict_to_df(results_dict,
                            key_column=SubmissionColumns.ID.value,
                            value_column=SubmissionColumns.QODANA_ISSUES.value)

    return df_results


def evaluate(df_solutions: pd.DataFrame, config: QodanaEvaluationConfig) -> pd.DataFrame:
    """ All solutions are grouped by language version and inspected by groups by qodana tool. """

    results = []

    for lang, df_lang_solutions in df_solutions.groupby(SubmissionColumns.LANG.value):
        lang_results = evaluate_solutions(df_lang_solutions, lang, config)
        results.append(lang_results)

    df_results = pd.concat(results)
    df_solutions = merge_dfs(df_solutions, df_results,
                             left_on=SubmissionColumns.ID.value,
                             right_on=SubmissionColumns.ID.value,
                             )
    return df_solutions


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    start = time.time()
    args = parser.parse_args()

    df_solutions = read_df(args.solutions_file_path)
    config = QodanaEvaluationConfig(with_custom_profile=args.with_custom_profile)

    logger.info('Start processing:')
    results = evaluate(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, QODANA_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, QODANA_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
