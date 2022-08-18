from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Union

from dataclasses_json import LetterCase, dataclass_json

from analysis.src.python.evaluation.model.report import BaseIssue, BaseReport
from analysis.src.python.utils.json_utils import parse_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Code:
    start_line: int
    length: int
    offset: int
    surrounding_code: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Source:
    type: str
    path: str
    language: str
    line: int
    offset: int
    length: int
    code: Code


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Attributes:
    inspection_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Problem(BaseIssue):
    tool: str
    category: str
    type: str
    severity: str
    comment: str
    details_info: str
    sources: List[Source]
    attributes: Attributes

    def get_name(self) -> str:
        return self.attributes.inspection_name

    def get_text(self) -> str:
        return self.comment

    def get_line_number(self) -> int:
        return self.sources[0].line

    def get_column_number(self) -> int:
        return self.sources[0].offset

    def get_category(self) -> str:
        return self.category

    def get_difficulty(self) -> str:
        return self.severity


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class QodanaReport(BaseReport):
    version: str
    list_problem: List[Problem]

    def get_issues(self) -> List[BaseIssue]:
        return self.list_problem

    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'QodanaReport':
        # TODO: recalculate quality after filtering
        return QodanaReport(list_problem=[issue for issue in self.list_problem if predicate(issue)],
                            version=self.version)

    @staticmethod
    def from_file(json_path: Union[Path, str]) -> 'QodanaReport':
        return QodanaReport.from_dict(parse_json(json_path))
