import json
from dataclasses import dataclass
from typing import List

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Source:
    type: str
    path: str
    language: str
    line: int
    offset: int
    length: int


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
    attributes:  Attributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class QodanaReport:
    version: str
    list_problem: List[Problem]

    def to_str(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_str(s: str) -> 'QodanaReport':
        return QodanaReport.from_dict(json.loads(s))
