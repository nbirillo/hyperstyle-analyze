from analysis.src.python.data_analysis.utils.analysis_issue import AnalysisReport
from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines


def calculate_issues_count(str_report: str) -> int:
    """ Parse issues list and calculate number of issues. """

    return len(AnalysisReport.from_json(str_report).issues)


def calculate_code_lines_count(code: str) -> int:
    """ Calculate number of code lines. """

    if isinstance(code, str):
        return len(split_code_to_lines(code))
    return 0


def calculate_code_symbols_count(code: str) -> int:
    """ Calculate number of symbols in code. """

    if isinstance(code, str):
        return len(code)
    return 0
