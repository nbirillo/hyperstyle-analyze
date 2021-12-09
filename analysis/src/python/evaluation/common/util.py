import os
import pickle
import re
import shutil
import subprocess
from enum import Enum, unique
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple, Union

import yaml
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.file_system import (
    Extension, get_all_file_system_items, ItemCondition,
)


@unique
class AnalysisExtension(Enum):
    XLSX = '.xlsx'
    CSV = '.csv'
    PICKLE = '.pickle'
    JSON = '.json'
    HTML = '.html'

    # Image extensions
    PNG = '.png'
    JPG = '.jpg'
    JPEG = '.jpeg'
    WEBP = '.webp'
    SVG = '.svg'
    PDF = '.pdf'
    EPS = '.eps'

    # Not empty extensions are returned with a dot, for example, '.txt'
    # If file has no extensions, an empty one ('') is returned
    @classmethod
    def get_extension_from_file(cls, file: Union[Path, str]) -> Union['AnalysisExtension', Extension]:
        ext = os.path.splitext(file)[1]
        try:
            return AnalysisExtension(ext)
        except ValueError:
            return Extension(ext)

    @classmethod
    def get_image_extensions(cls) -> List[Union[Extension, 'AnalysisExtension']]:
        return [
            AnalysisExtension.PNG,
            AnalysisExtension.JPG,
            AnalysisExtension.JPEG,
            AnalysisExtension.WEBP,
            AnalysisExtension.SVG,
            AnalysisExtension.PDF,
            AnalysisExtension.EPS,
        ]


@unique
class ColumnName(Enum):
    CODE = 'code'
    LANG = 'lang'
    LANGUAGE = 'language'
    GRADE = 'grade'
    ID = 'id'
    COLUMN = 'column'
    ROW = 'row'
    OLD = 'old'
    NEW = 'new'
    IS_PUBLIC = 'is_public'
    DECREASED_GRADE = 'decreased_grade'
    PENALTY = 'penalty'
    USER = 'user'
    HISTORY = 'history'
    TIME = 'time'
    TRACEBACK = 'traceback'


@unique
class EvaluationArgument(Enum):
    TRACEBACK = 'traceback'
    RESULT_FILE_NAME = 'evaluation_results'
    RESULT_FILE_NAME_XLSX = f'{RESULT_FILE_NAME}{AnalysisExtension.XLSX.value}'
    RESULT_FILE_NAME_CSV = f'{RESULT_FILE_NAME}{AnalysisExtension.CSV.value}'


script_structure_rule = ('Please, make sure your XLSX-file matches following script standards: \n'
                         '1. Your XLSX-file or CSV-file should have 2 obligatory columns named:'
                         f'"{ColumnName.CODE.value}" & "{ColumnName.LANG.value}". \n'
                         f'"{ColumnName.CODE.value}" column -- relates to the code-sample. \n'
                         f'"{ColumnName.LANG.value}" column -- relates to the language of a '
                         'particular code-sample. \n'
                         '2. Your code samples should belong to the one of the supported languages. \n'
                         'Supported languages are: Java, Kotlin, Python. \n'
                         f'3. Check that "{ColumnName.LANG.value}" column cells are filled with '
                         'acceptable language-names: \n'
                         f'Acceptable language-names are: {LanguageVersion.PYTHON_3.value}, '
                         f'{LanguageVersion.JAVA_8.value} ,'
                         f'{LanguageVersion.JAVA_11.value} and {LanguageVersion.KOTLIN.value}.')


# Split string by separator
def parse_set_arg(str_arg: str, separator: str = ',') -> Set[str]:
    return set(str_arg.split(separator))


def get_in_and_out_list(root: Path,
                        in_ext: Union[Extension, AnalysisExtension] = AnalysisExtension.CSV,
                        out_ext: Union[Extension, AnalysisExtension]
                        = AnalysisExtension.CSV) -> List[Tuple[Path, Path]]:
    in_files = get_all_file_system_items(root, match_condition(rf'in_\d+{in_ext.value}'))
    out_files = get_all_file_system_items(root, match_condition(rf'out_\d+{out_ext.value}'))
    return pair_in_and_out_files(in_files, out_files)


def run_in_subprocess_with_working_dir(command: List[str], working_dir: str) -> str:
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir,
    )

    stdout = process.stdout.decode()

    return stdout


def run_and_wait(command: List[str]) -> None:
    process = subprocess.Popen(command)
    process.wait()


def get_restricted_extension(file_path: Optional[Union[str, Path]] = None,
                             available_values: List[Union[Extension, AnalysisExtension]]
                             = None) -> Union[Extension, AnalysisExtension]:
    if file_path is None:
        return Extension.EMPTY
    ext = AnalysisExtension.get_extension_from_file(file_path)
    if available_values is not None and ext not in available_values:
        raise ValueError(f'Invalid extension. '
                         f'Available values are: {list(map(lambda e: e.value, available_values))}.')
    return ext


def extension_file_condition(extension: Union[Extension, AnalysisExtension]) -> ItemCondition:
    def has_this_extension(name: str) -> bool:
        return Extension.get_extension_from_file(name) == extension or AnalysisExtension.get_extension_from_file(
            name) == extension

    return has_this_extension


def match_condition(regex: str) -> ItemCondition:
    def does_name_match(name: str) -> bool:
        return re.fullmatch(regex, name) is not None

    return does_name_match


def serialize_data_and_write_to_file(path: Path, data: Any) -> None:
    os.makedirs(get_parent_folder(path), exist_ok=True)
    with open(path, 'wb') as f:
        p = pickle.Pickler(f)
        p.dump(data)


def deserialize_data_from_file(path: Path) -> Any:
    with open(path, 'rb') as f:
        u = pickle.Unpickler(f)
        return u.load()


def parse_yaml(path: Union[Path, str]) -> Any:
    with open(path) as file:
        return yaml.safe_load(file)


# For getting name of the last folder or file
# For example, returns 'folder' for both 'path/data/folder' and 'path/data/folder/'
def get_name_from_path(path: Union[Path, str], with_extension: bool = True) -> str:
    head, tail = os.path.split(path)
    # Tail can be empty if '/' is at the end of the path
    file_name = tail or os.path.basename(head)
    if not with_extension:
        file_name = os.path.splitext(file_name)[0]
    elif AnalysisExtension.get_extension_from_file(file_name) == Extension.EMPTY:
        raise ValueError('Cannot get file name with extension, because the passed path does not contain it')
    return file_name


def pair_in_and_out_files(in_files: List[Path], out_files: List[Path]) -> List[Tuple[Path, Path]]:
    pairs = []
    for in_file in in_files:
        out_file = Path(re.sub(r'in(?=[^in]*$)', 'out', str(in_file)))
        if out_file not in out_files:
            raise ValueError(f'List of out files does not contain a file for {in_file}')
        pairs.append((in_file, out_file))
    return pairs


# File should contain the full path and its extension.
# Create all parents if necessary
def create_file(file_path: Union[str, Path], content: str):
    file_path = Path(file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w+') as f:
        f.writelines(content)
        yield Path(file_path)


def copy_file(source: Union[str, Path], destination: Union[str, Path]):
    shutil.copy(source, destination)


def copy_directory(source: Union[str, Path], destination: Union[str, Path], dirs_exist_ok: bool = True):
    shutil.copytree(source, destination, dirs_exist_ok=dirs_exist_ok)


def get_parent_folder(path: Union[Path, str], to_add_slash: bool = False) -> Path:
    path = remove_slash(str(path))
    parent_folder = '/'.join(path.split('/')[:-1])
    if to_add_slash:
        parent_folder = add_slash(parent_folder)
    return Path(parent_folder)


def add_slash(path: str) -> str:
    if not path.endswith('/'):
        path += '/'
    return path


def remove_slash(path: str) -> str:
    return path.rstrip('/')


def remove_directory(directory: Union[str, Path]) -> None:
    if os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)
