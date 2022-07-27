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
from analysis.src.python.evaluation.utils.evaluation_utils import evaluate_by_language
from analysis.src.python.evaluation.utils.solutions_saving_utils import get_solution_id_by_file_path
from analysis.src.python.utils.df_utils import dict_to_df, read_df, write_df
from analysis.src.python.utils.file_utils import get_output_filename, get_output_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

QODANA_OUTPUT_SUFFIX = '_qodana'


def parse_qodana_result(result_path: Path) -> pd.DataFrame:
    """ Parse results for group of solution and split by solution id. """

    results_dict = defaultdict(list)

    try:
        with open(result_path, 'r') as f:
            report = QodanaReport.from_str(f.read())

        for problem in report.list_problem:
            if len(problem.sources) != 1:
                logging.warning(f'Skipping multi source problem {problem}')
            solution_id = get_solution_id_by_file_path(problem.sources[0].path)
            results_dict[solution_id].append(problem)

        results_dict = {i: QodanaReport(report.version, problems).to_str()
                        for i, problems in results_dict.items()}

    except Exception as e:
        logging.error(f"Can not parse report from qodana output: {e}")

    return dict_to_df(results_dict,
                      key_column=SubmissionColumns.ID.value,
                      value_column=SubmissionColumns.QODANA_ISSUES.value)


def evaluate_qodana(df_solutions: pd.DataFrame, config: QodanaEvaluationConfig) -> pd.DataFrame:
    """ Run qodana on set of solutions. """

    df_solutions = evaluate_by_language(df_solutions, config, parse_qodana_result)
    return df_solutions


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    start = time.time()
    args = parser.parse_args()

    df_solutions = read_df(args.solutions_file_path)
    config = QodanaEvaluationConfig(with_custom_profile=args.with_custom_profile,
                                    tmp_directory=args.tmp_directory)

    logger.info('Start processing:')
    results = evaluate_qodana(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, QODANA_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, QODANA_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
