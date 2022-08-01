from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

from dataclasses_json import LetterCase, dataclass_json

from analysis.src.python.utils.json_utils import parse_json

from analysis.src.python.utils.json_utils import parse_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Code:
    start_line: int
    length: int
    offset: int
    surrounding_code: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Code:
    start_line: int
    length: int
    offset: int
    surrounding_code: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Source:
    type: str
    path: str
    language: str
    line: int
    offset: int
    length: int
    code: Code


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Attributes:
    inspection_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Problem:
    tool: str
    category: str
    type: str
    severity: str
    comment: str
    details_info: str
    sources: List[Source]
    attributes: Attributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class QodanaReport:
    version: str
    list_problem: List[Problem]

    @staticmethod
    def from_file(json_path: Union[Path, str]) -> 'QodanaReport':
        return QodanaReport.from_dict(parse_json(json_path))
