from analysis.src.python.data_analysis.utils.code_utils import split_code_to_lines
from analysis.src.python.evaluation.tools.utils.parsing_utils import parse_str_report


def calculate_issues_count(str_report: str, issues_column: str) -> int:
    """ Parse issues list and calculate number of issues. """

    return len(parse_str_report(str_report, issues_column).get_issues())


def calculate_code_lines_count(code: str, ignore_empty_lines: bool = False) -> int:
    """ Calculate number of code lines. """

    if isinstance(code, str):
        lines = split_code_to_lines(code)

        if ignore_empty_lines:
            lines = list(filter(lambda line: line.strip() != '', lines))

        return len(lines)

    return 0


def calculate_code_symbols_count(code: str) -> int:
    """ Calculate number of symbols in code. """

    if isinstance(code, str):
        return len(code)
    return 0
