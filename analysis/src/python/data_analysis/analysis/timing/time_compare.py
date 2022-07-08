import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.language import Language
from hyperstyle.src.python.review.reviewers.common import LANGUAGE_TO_INSPECTORS

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.utils.df_utils import read_df
from analysis.src.python.utils.logging_utils import configure_logger
from analysis.src.python.utils.file_utils import create_file
from analysis.src.python.utils.parallel_utils import run_and_wait

SRC_FOLDER = Path(__file__).parents[4] / 'resources' / 'evaluation' / 'qodana'
TEMPLATE_FOLDER = SRC_FOLDER / 'project_templates'
PROFILE_FOLDER = SRC_FOLDER / 'inspection_profiles'
JAVA_QODANA_IMAGE_PATH = 'jetbrains/qodana'
PYTHON_QODANA_IMAGE_PATH = 'jetbrains/qodana-python'


def write_code_to_template(language: LanguageVersion, code: str):
    if language.is_java():
        project_dir = TEMPLATE_FOLDER / 'java'
        main_path = project_dir / 'src/main/java/Main.java'
    elif language == LanguageVersion.PYTHON_3:
        project_dir = TEMPLATE_FOLDER / 'python'
        main_path = project_dir / 'main.py'
    else:
        raise NotImplementedError(f'{language} needs implementation.')

    create_file(main_path, code)
    return project_dir, main_path


def get_qodana_configuration(language: LanguageVersion):
    if language.is_java():
        qodana_image_path = 'jetbrains/qodana'
        profile_path = PROFILE_FOLDER / 'java_profile.xml'
    elif language == LanguageVersion.PYTHON_3:
        qodana_image_path = 'jetbrains/qodana-python'
        profile_path = PROFILE_FOLDER / 'python_profile.xml'
    else:
        raise NotImplementedError(f'{language} needs implementation.')

    return qodana_image_path, profile_path


def measure_run_time(f: Callable[[], Any], repeat: int) -> float:
    repeat_times = []

    for i in range(repeat):
        logging.info(f'Time measuring attempt={i}')

        start_time = time.time()
        f()
        end_time = time.time()

        repeat_times.append(end_time - start_time)

    return np.array(repeat_times).mean()


def measure_hyperstyle_time(language: str, code: str, repeat: int = 5) -> float:
    language_version = LanguageVersion.from_value(language)

    language = Language.from_language_version(language_version)
    inspectors = LANGUAGE_TO_INSPECTORS.get(language, [])

    inspectors_config = {
        'language_version': language_version,
        'n_cpu': 1,
    }

    project_dir, main_path = write_code_to_template(language_version, code)

    def run_hyperstyle():
        for inspector in inspectors:
            inspector.inspect(main_path, inspectors_config)

    logging.info('Measure hyperstyle time')
    return measure_run_time(run_hyperstyle, repeat)


def measure_qodana_time(language: str, code: str, repeat: int = 5) -> float:
    language_version = LanguageVersion.from_value(language)

    results_dir = 'result'
    qodana_image_path, profile_path = get_qodana_configuration(language_version)
    project_dir, main_path = write_code_to_template(language_version, code)

    command = [
        'docker', 'run',
        '-u', str(os.getuid()),
        '--rm',
        '-v', f'{Path(project_dir).resolve()}/:/data/project/',
        '-v', f'{Path(results_dir).resolve()}/:/data/results/',
        '-v', f'{Path(profile_path).resolve()}:/data/profile.xml',
        f'{qodana_image_path}',
    ]

    def run_qodana():
        run_and_wait(command)

    logging.info('Measure qodana time')
    return measure_run_time(run_qodana, repeat)


def time_evaluation(submissions_path: str, time_evaluation_path: str, repeat: int):
    """ Runs qode quality analyzers on """

    df_submissions = read_df(submissions_path)

    result = {
        'id': [],
        'hyperstyle': [],
        'qodana': [],
    }

    for i, submissions in df_submissions.iterrows():
        logging.info(f'Timing iteration {i}-th submission with id={submissions[SubmissionColumns.ID.value]}')

        result['id'].append(submissions[SubmissionColumns.ID.value])
        result['hyperstyle'].append(
            measure_hyperstyle_time(submissions[SubmissionColumns.LANG.value],
                                    submissions[SubmissionColumns.CODE.value], repeat))
        result['qodana'].append(
            measure_qodana_time(submissions[SubmissionColumns.LANG.value],
                                submissions[SubmissionColumns.CODE.value], repeat))

    pd.DataFrame.from_dict(result).to_csv(time_evaluation_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions samples')
    parser.add_argument('time_stats_path', type=str,
                        help='Path to .csv file with linters timing statistics')
    parser.add_argument('--repeat', default=3, type=int,
                        help='Times to repeat time evaluation for averaging')

    args = parser.parse_args(sys.argv[1:])

    configure_logger(args.time_stats_path, 'timing')

    time_evaluation(args.submissions_path,
                    args.time_stats_path,
                    args.repeat)
