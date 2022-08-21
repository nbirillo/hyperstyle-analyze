import os
from typing import List, Optional

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.report_utils import parse_report
from analysis.src.python.evaluation.tools.model.report import BaseIssue
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version

WINDOWS_LINE_ENDING = '\r\n'
LINUX_LINE_ENDING = '\n'


def get_comment_symbol(language_version: LanguageVersion):
    if language_version.is_java():
        return '//'
    if language_version == LanguageVersion.PYTHON_3:
        return '#'

    raise NotImplementedError(f'Comment symbol for language version {language_version.value} is not defined.')


def get_comment_to_code_line(issue: BaseIssue, language_version: LanguageVersion) -> str:
    """ Get comment with information about given issue. """
    comment_symbol = get_comment_symbol(language_version)
    return f' {comment_symbol} {issue.get_name()} line={issue.get_line_number()} offset={issue.get_column_number()}'


def get_code_with_issue_comment(submission: pd.Series, issues_column: str, issue_name: Optional[str]) -> str:
    """ Add comment to code lines where issues appear in submission. """

    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
    language_version = get_language_version(submission[SubmissionColumns.LANG.value])

    report = parse_report(submission, issues_column)
    for issue in report.get_issues():
        if issue_name is None or issue.get_name() == issue_name:
            code_lines[issue.get_line_number() - 1] += get_comment_to_code_line(issue, language_version)

    return merge_lines_to_code(code_lines)


def split_code_to_lines(code: str) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without \r). """
    code = code.replace(WINDOWS_LINE_ENDING, os.linesep)
    code = code.replace(LINUX_LINE_ENDING, os.linesep)

    return code.split(os.linesep)


def merge_lines_to_code(code_lines: List[str]) -> str:
    """ Merge lines to code. """

    return os.linesep.join(code_lines)
