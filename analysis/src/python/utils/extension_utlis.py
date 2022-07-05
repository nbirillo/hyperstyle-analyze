import os
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional, Union

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
        try:
            return AnalysisExtension.get_extension_from_file(name) == extension
        except ValueError:
            return False

    return has_this_extension
