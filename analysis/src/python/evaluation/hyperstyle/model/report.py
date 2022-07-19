from dataclasses import dataclass
from typing import List


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
class HyperstyleFileReport:
    file_name: str
    quality: Quality
    issues: List[HyperstyleIssue]


@dataclass(frozen=True)
class HyperstyleReport:
    quality: Quality
    file_review_results: List[HyperstyleFileReport]
