import os
from pathlib import Path

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.file_utils import create_directory, create_file


def save_solution_to_file(solution: pd.Series, dst_directory: Path) -> Path:
    """ Save solution code to file dst_directory/solution_{ID}/code.{EXT} """

    solution_id = solution[SubmissionColumns.ID.value]
    code = solution[SubmissionColumns.CODE.value]
    language = solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(language)

    solution_dir_path = dst_directory / str(solution_id)
    create_directory(solution_dir_path)
    os.chmod(solution_dir_path, 0o777)

    solution_file_path = solution_dir_path / f'code{language_version.extension_by_language().value}'
    solution_file_path = next(create_file(solution_file_path, code))
    os.chmod(solution_file_path, 0o777)

    return solution_file_path
