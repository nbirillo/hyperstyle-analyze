import os
from pathlib import Path
from typing import Optional

import pytest
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.file_system import get_content_from_file
from hyperstyle.src.python.review.common.subprocess_runner import run_in_subprocess
from analysis.src.python.evaluation.evaluation_config import EvaluationConfig
from analysis.test.python.common import FILE_SYSTEM_DATA_FOLDER
from analysis.test.python.evaluation.testing_config import get_testing_arguments
from analysis.src.python.evaluation.common.file_util import create_file

INPUT_DATA = [
    ('in_1.java', LanguageVersion.JAVA_11),
    ('in_2.py', LanguageVersion.PYTHON_3),
]


def inspect_code(config: EvaluationConfig, file: str, language: LanguageVersion, history: Optional[str] = None) -> str:
    command = config.build_command(file, language.value, history)
    return run_in_subprocess(command)


@pytest.mark.parametrize(('test_file', 'language'), INPUT_DATA)
def test_synthetic_files(test_file: str, language: LanguageVersion):
    input_file = FILE_SYSTEM_DATA_FOLDER / test_file
    test_args = get_testing_arguments(to_add_traceback=True, to_add_tool_path=True)
    config = EvaluationConfig(test_args)

    expected_output = inspect_code(config, input_file, language)

    input_code = get_content_from_file(Path(input_file))
    actual_file = next(create_file(FILE_SYSTEM_DATA_FOLDER / f'actual_file{language.extension_by_language().value}',
                                   input_code))

    actual_output = inspect_code(config, actual_file, language)
    os.remove(actual_file)

    assert actual_output == expected_output
