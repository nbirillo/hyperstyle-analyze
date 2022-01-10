import ast


def calc_issues_count(issues: str) -> int:
    """ Parse issues list and calculate number of issues. """

    return len(ast.literal_eval(issues))


def calculate_code_lines_count(code: str) -> int:
    """ Calculate number of code lines. """

    if isinstance(code, str):
        return len(code.split('\n'))
    return 0


def calculate_code_symbols_count(code: str) -> int:
    """ Calculate number of symbols in code. """

    if isinstance(code, str):
        return len(code)
    return 0
