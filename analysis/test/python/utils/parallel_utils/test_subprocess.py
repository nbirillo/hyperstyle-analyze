import os
from pathlib import Path
from typing import Optional

import pytest
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.file_system import get_content_from_file

from analysis.src.python.evaluation.evaluation_config import EvaluationConfig
from analysis.src.python.utils.parallel_utils import run_in_subprocess_with_working_dir
from analysis.test.python.evaluation.testing_config import get_testing_arguments
from analysis.src.python.utils.file_utils import create_file
from analysis.test.python.utils import PARALLEL_UTILS_DATA_FOLDER

RESOURCES_PATH = PARALLEL_UTILS_DATA_FOLDER / 'subprocess'

INPUT_DATA = [
    ('in_1.java', LanguageVersion.JAVA_11),
    ('in_2.py', LanguageVersion.PYTHON_3),
]


def inspect_code(config: EvaluationConfig, file: str, language: LanguageVersion, history: Optional[str] = None) -> str:
    command = config.build_command(file, language.value, history)
    return run_in_subprocess_with_working_dir(command, config.get_tool_root())


@pytest.mark.parametrize(('test_file', 'language'), INPUT_DATA)
def test(test_file: str, language: LanguageVersion):
    input_file = RESOURCES_PATH / test_file
    test_args = get_testing_arguments(to_add_traceback=True, to_add_tool_path=True)
    config = EvaluationConfig(test_args)

    expected_output = inspect_code(config, input_file, language)

    input_code = get_content_from_file(Path(input_file))
    actual_file = next(create_file(RESOURCES_PATH / f'actual_file{language.extension_by_language().value}',
                                   input_code))

    actual_output = inspect_code(config, actual_file, language)
    os.remove(actual_file)

    assert actual_output == expected_output
