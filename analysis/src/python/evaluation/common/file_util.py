import os
import pickle
import re
import shutil
from enum import Enum, unique
from pathlib import Path
from typing import Any, List, Optional, Union

from hyperstyle.src.python.review.common.file_system import Extension, ItemCondition


@unique
class AnalysisExtension(Enum):
    XLSX = '.xlsx'
    CSV = '.csv'
    PICKLE = '.pickle'
    JSON = '.json'
    HTML = '.html'
    TXT = '.txt'

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


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


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
