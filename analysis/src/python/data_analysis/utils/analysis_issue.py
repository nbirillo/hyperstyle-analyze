from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.evaluation.hyperstyle.model.report import HyperstyleIssue, HyperstyleReport
from analysis.src.python.evaluation.qodana.model.report import Problem, QodanaReport


@dataclass_json
@dataclass(frozen=True, eq=True)
class AnalysisIssue:
    name: str
    text: str
    line_number: int
    column_number: int
    category: str
    difficulty: str

    @staticmethod
    def from_qodana_issue(problem: Problem) -> 'AnalysisIssue':
        return AnalysisIssue(
            name=problem.attributes.inspection_name,
            text=problem.comment,
            line_number=problem.sources[0].line,
            column_number=problem.sources[0].offset,
            category=problem.category,
            difficulty=problem.severity,
        )

    @staticmethod
    def from_hyperstyle_issue(issue: HyperstyleIssue) -> 'AnalysisIssue':
        return AnalysisIssue(
            name=issue.code,
            text=issue.text,
            line_number=issue.line_number,
            column_number=issue.column_number,
            category=issue.category,
            difficulty=issue.difficulty,
        )


@dataclass_json
@dataclass
class AnalysisReport:
    issues: List[AnalysisIssue]

    @staticmethod
    def from_qodana_report(str_report: str) -> 'AnalysisReport':
        report = QodanaReport.from_json(str_report)
        return AnalysisReport(issues=list(map(AnalysisIssue.from_qodana_issue, report.list_problem)))

    @staticmethod
    def from_hyperstyle_report(str_report: str) -> 'AnalysisReport':
        report = HyperstyleReport.from_json(str_report)
        return AnalysisReport(issues=list(map(AnalysisIssue.from_hyperstyle_issue, report.issues)))

    @staticmethod
    def from_json_report(str_report: str, column: str) -> 'AnalysisReport':
        if column == SubmissionColumns.HYPERSTYLE_ISSUES.value:
            return AnalysisReport.from_hyperstyle_report(str_report)
        if column == SubmissionColumns.QODANA_ISSUES.value:
            return AnalysisReport.from_qodana_report(str_report)

        raise NotImplementedError(f'Implement parser for issue stored in column: {column}')

    @staticmethod
    def convert_to_analysis_json_report(str_report: str, column: str):
        report = AnalysisReport.from_json_report(str_report, column)
        return report.to_json()

    def has_issue(self, issue_name: str) -> bool:
        for issue in self.issues:
            if issue.name == issue_name:
                return True
        return False
