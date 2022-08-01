import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dataclasses_json import dataclass_json

from analysis.src.python.utils.json_utils import parse_json


@dataclass_json
@dataclass(frozen=True)
class Quality:
    code: str
    text: str


@dataclass_json
@dataclass(frozen=True)
class HyperstyleIssue:
    code: str
    text: str
    line: str
    line_number: int
    column_number: int
    category: str
    difficulty: str
    influence_on_penalty: int


@dataclass_json
@dataclass(frozen=True)
class QualityReport:
    quality: Quality

    def to_str(self) -> str:
        return json.dumps(self.to_dict())


@dataclass_json
@dataclass(frozen=True)
class HyperstyleReport(QualityReport):
    issues: List[HyperstyleIssue]

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleReport':
        return HyperstyleReport.from_dict(parse_json(json_path))


@dataclass_json
@dataclass(frozen=True)
class HyperstyleFileReport(HyperstyleReport):
    file_name: str

    def to_hyperstyle_report(self) -> HyperstyleReport:
        return HyperstyleReport(self.quality, self.issues)


@dataclass_json
@dataclass(frozen=True)
class HyperstyleNewFormatReport(QualityReport):
    file_review_results: List[HyperstyleFileReport]

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleNewFormatReport':
        return HyperstyleNewFormatReport.from_dict(parse_json(json_path))
