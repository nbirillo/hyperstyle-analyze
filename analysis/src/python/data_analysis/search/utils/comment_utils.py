from typing import Optional

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.analysis_issue import parse_report
from analysis.src.python.data_analysis.utils.code_utils import merge_lines_to_code, split_code_to_lines
from analysis.src.python.evaluation.utils.pandas_utils import get_language_version


def get_comment_symbol(language_version: LanguageVersion) -> str:
    if language_version.is_java():
        return ' //'
    if language_version == LanguageVersion.PYTHON_3:
        return ' #'

    raise NotImplementedError(f'Comment for language version {language_version.value} is not defined.')


def get_issue_comment(language_version: LanguageVersion,
                      issue_name: str, line_number: int, column_number: Optional[int] = None) -> str:
    """ Add comment to given code line. """

    comment_symbol = get_comment_symbol(language_version)
    comment = f'{comment_symbol} {issue_name} line={line_number}'

    if column_number is not None:
        comment += f' offset={column_number}'

    return comment


def add_issues_comments_to_code(submission: pd.Series, issues_column: str,
                                issue_name: Optional[str] = None) -> pd.Series:
    """ Add comment to row where specific issue appears in solution. """

    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])

    report = parse_report(submission, issues_column)
    lang = submission[SubmissionColumns.LANG.value]

    for issue in report.issues:
        if issue_name is None or issue.name == issue_name:
            language_version = get_language_version(lang)
            comment = get_issue_comment(language_version, issue.name, issue.line_number, issue.column_number)
            code_lines[issue.line_number - 1] += comment

    submission[SubmissionColumns.CODE.value] = merge_lines_to_code(code_lines)

    return submission
