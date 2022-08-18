import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from dataclasses_json import dataclass_json

from analysis.src.python.evaluation.model.report import BaseIssue, BaseReport
from analysis.src.python.utils.json_utils import parse_json


@dataclass_json
@dataclass(frozen=True, eq=True)
class Quality:
    code: str
    text: str


@dataclass_json
@dataclass(frozen=True)
class HyperstyleIssue(BaseIssue):
    code: str
    text: str
    line: str
    line_number: int
    column_number: int
    category: str
    difficulty: str
    influence_on_penalty: int

    def get_name(self) -> str:
        return self.code

    def get_text(self) -> str:
        return self.text

    def get_line_number(self) -> int:
        return self.line_number

    def get_column_number(self) -> int:
        return self.column_number

    def get_category(self) -> str:
        return self.category

    def get_difficulty(self) -> str:
        return self.difficulty


@dataclass_json
@dataclass(frozen=True, eq=True)
class QualityReport:
    quality: Quality

    def to_str(self) -> str:
        return json.dumps(self.to_dict())


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleReport(QualityReport, BaseReport):
    issues: List[HyperstyleIssue]

    def get_issues(self) -> List[BaseIssue]:
        return self.issues

    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'HyperstyleReport':
        # TODO: recalculate quality after filtering
        return HyperstyleReport(issues=[issue for issue in self.issues if predicate(issue)],
                                quality=self.quality)

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleReport':
        return HyperstyleReport.from_dict(parse_json(json_path))


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleFileReport(HyperstyleReport):
    file_name: str

    def to_hyperstyle_report(self) -> HyperstyleReport:
        return HyperstyleReport(self.quality, self.issues)


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleNewFormatReport(QualityReport):
    file_review_results: List[HyperstyleFileReport]

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleNewFormatReport':
        return HyperstyleNewFormatReport.from_dict(parse_json(json_path))
