import os
from pathlib import Path

import pytest
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.file_system import get_content_from_file

from analysis import HYPERSTYLE_RUNNER_PATH
from analysis.src.python.evaluation.hyperstyle.evaluate import run_evaluation_command
from analysis.src.python.evaluation.hyperstyle.evaluation_config import HyperstyleEvaluationConfig
from analysis.src.python.utils.file_utils import create_file
from analysis.test.python.utils import PARALLEL_UTILS_DATA_FOLDER

RESOURCES_PATH = PARALLEL_UTILS_DATA_FOLDER / 'subprocess'

INPUT_DATA = [
    ('in_1.java', LanguageVersion.JAVA_11),
    ('in_2.py', LanguageVersion.PYTHON_3),
]


def inspect_code(config: HyperstyleEvaluationConfig, file: Path, language: LanguageVersion) -> str:
    command = config.build_command(file, language)
    return run_evaluation_command(command)


@pytest.mark.parametrize(('test_file', 'language'), INPUT_DATA)
def test(test_file: str, language: LanguageVersion):
    input_file = RESOURCES_PATH / test_file
    config = HyperstyleEvaluationConfig(docker_path=None,
                                        tool_path=HYPERSTYLE_RUNNER_PATH,
                                        allow_duplicates=False,
                                        with_all_categories=False,
                                        new_format=True,
                                        )

    expected_output = inspect_code(config, input_file, language)

    input_code = get_content_from_file(Path(input_file))
    actual_file = next(create_file(RESOURCES_PATH / f'actual_file{language.extension_by_language().value}',
                                   input_code))

    actual_output = inspect_code(config, actual_file, language)
    os.remove(actual_file)

    assert actual_output == expected_output
