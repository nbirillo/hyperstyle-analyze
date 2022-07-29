import ast
import os


def calculate_issues_count(issues: str) -> int:
    """ Parse issues list and calculate number of issues. """

    return len(ast.literal_eval(issues))


def calculate_code_lines_count(code: str, ignore_empty_lines: bool = False) -> int:
    """ Calculate number of code lines. """

    if isinstance(code, str):
        lines = code.split(os.linesep)

        if ignore_empty_lines:
            lines = list(filter(lambda line: line.strip() != '', lines))

        return len(lines)

    return 0


def calculate_code_symbols_count(code: str) -> int:
    """ Calculate number of symbols in code. """

    if isinstance(code, str):
        return len(code)
    return 0
