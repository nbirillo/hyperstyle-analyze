import dataclasses
import json
from dataclasses import dataclass
from typing import List

from dacite import from_dict


@dataclass(frozen=True)
class Quality:
    code: str
    text: str


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


@dataclass(frozen=True)
class QualityReport:
    quality: Quality

    def to_str(self):
        return json.dumps(dataclasses.asdict(self))


@dataclass(frozen=True)
class HyperstyleReport(QualityReport):
    issues: List[HyperstyleIssue]

    @staticmethod
    def from_str(report: str):
        return from_dict(data_class=HyperstyleReport, data=json.loads(report))


@dataclass(frozen=True)
class HyperstyleFileReport(HyperstyleReport):
    file_name: str

    def to_hyperstyle_report(self):
        return HyperstyleReport(self.quality, self.issues)


@dataclass(frozen=True)
class HyperstyleNewFormatReport(QualityReport):
    file_review_results: List[HyperstyleFileReport]

    @staticmethod
    def from_str(report: str):
        return from_dict(data_class=HyperstyleNewFormatReport, data=json.loads(report))
