import os
from ctypes import Union
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version
from analysis.src.python.utils.file_utils import copy_directory, create_file, get_parent_folder

TEMPLATE_DIRECTORY = Path(__file__).parents[3] / 'resources' / 'evaluation' / 'project_templates'


@dataclass(frozen=True)
class TemplateConfig:
    template_path: Path
    template_root: Path
    filename: str


def get_template_config(language_version: LanguageVersion) -> TemplateConfig:
    if language_version.is_java():
        return TemplateConfig(template_path=TEMPLATE_DIRECTORY / 'java',
                              template_root=Path('src', 'main', 'java'),
                              filename='Main')

    elif language_version == LanguageVersion.PYTHON_3:
        return TemplateConfig(template_path=TEMPLATE_DIRECTORY / 'python',
                              template_root=Path(),
                              filename='main')

    raise NotImplementedError(f"Template is not provided for language {language_version.value}. "
                              f"Please implement template in {TEMPLATE_DIRECTORY}")


def save_solutions_to_files(df_solutions: pd.DataFrame,
                            language_version: LanguageVersion,
                            input_path: Path,
                            with_template: bool = False):
    """
    Save solutions to input_path.
    If with_template=True copy language version specific template to input_path.
    Save given solutions to input_path according to structure described in `configure_solution_file` method.
    """

    if with_template:
        # If template is required copy project template to input directory
        template_config = get_template_config(language_version)
        copy_directory(template_config.template_path, input_path)

        # Template set language specific requirements for solutions directory and filenames
        df_solutions.apply(save_solution_to_file,
                           input_path=input_path / template_config.template_root,
                           filename=template_config.filename,
                           axis=1)

    else:
        df_solutions.apply(save_solution_to_file,
                           input_path=input_path,
                           axis=1)


def save_solution_to_file(solution: pd.Series,
                          input_path: Path,
                          filename: str = 'code') -> Path:
    """
    Save solution code to file with path: input_path / root_path / solution_{solution_id} / filename.extension where:
    root_path = default_root_path by default but can be changes according to solution language version template
    filename = default_filename by default but can be changes according to solution language version template
    extension is selected according to solution language version

    Examples:
    java11 file with template: input_path/src/main/java/solution_12/Main.java
    java11 file without template: input_path/solution_12/code.java

    python3 file with template: input_path/solution_13/main.py
    python3 file without template: input_path/solution_13/code.py

    js file without template: input_path/solution_14/code.js
    """

    solution_id = solution[SubmissionColumns.ID.value]
    solution_code = solution[SubmissionColumns.CODE.value]
    lang = solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(lang)
    extension = language_version.extension_by_language()

    solution_file_path = input_path / f'solution_{solution_id}' / f'{filename}{extension.value}'

    solution_file_path = next(create_file(solution_file_path, solution_code))
    os.chmod(solution_file_path, 0o777)

    return solution_file_path


def get_solution_id_by_file_path(solution_file_path: str) -> int:
    """
    As solution is store like input_path / root_path / solution_{solution_id} / filename.extension
    we can easily parse solution id from file_path.
    """

    parent_directory = get_parent_folder(solution_file_path)
    _, solution_id = parent_directory.name.split('_')
    return int(solution_id)
