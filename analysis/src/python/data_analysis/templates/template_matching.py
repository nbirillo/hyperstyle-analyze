from math import floor
from typing import Callable, List, Optional, Tuple


def edit_distance(first_string: str, second_string: str) -> int:
    """ Compute edit distance for two strings. """

    n = len(first_string) + 1
    m = len(second_string) + 1
    dp = [[0 for _ in range(m)] for _ in range(n)]
    for i in range(1, n):
        dp[i][0] = i
    for j in range(1, m):
        dp[0][j] = j

    for i in range(1, n):
        for j in range(1, m):
            d = 0 if first_string[i - 1] == second_string[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + d, dp[i - 1][j] + 1, dp[i][j - 1] + 1)

    return dp[n - 1][m - 1]


def equal_char_by_char(code_line: str, template_line: str) -> bool:
    """ Consider two lines are equal if they are equal char by char. """
    return code_line == template_line


def equal_edit_distance(code_line: str, template_line: str, upper_bound: int = 3) -> bool:
    """ Consider two strings as equal if their edit distance is no more than upper_bound. """
    return edit_distance(code_line, template_line) <= upper_bound


def equal_edit_ratio(code_line: str, template_line: str, upper_ration: float = 0.2) -> bool:
    """ Consider two strings as equal if their edit distance is no more than upper_ration of max of strings length. """
    return equal_edit_distance(code_line, template_line, floor(max(len(code_line), len(template_line)) * upper_ration))


def remove_single_comment(line: str, comment_symbol: str):
    """ Remove single comments (like // or #). """

    return line.split(comment_symbol)[0]


def remove_double_comment(line: str, start_comment_symbol: str, end_comment_symbol: str):
    """ Remove double comments (like /*...*/ or \"\"\"...\"\"\"). """

    return line.split(start_comment_symbol)[0] + line.split(end_comment_symbol)[-1]


def remove_comment(line: str):
    """ Remove all types of comments. """
    if '//' in line:
        line = remove_single_comment(line, '//')
    if '/*' in line and '*/' in line:
        line = remove_double_comment(line, '/*', '*/')
    if '#' in line:
        line = remove_single_comment(line, '#')
    if '""""' in line:
        line = remove_double_comment(line, '""""', '""""')

    return line


def equal_substring(code_line: str, template_line: str) -> bool:
    """ Consider two lines are equal if they after comments removing template line is substring of code line. """
    code_line = remove_comment(code_line)
    template_line = remove_comment(template_line)

    return template_line in code_line


EQUAL = {
    'char_by_char': equal_char_by_char,
    'edit_distance': equal_edit_distance,
    'edit_ratio': equal_edit_distance,
    'substring': equal_substring,
}


def match_empty_lines(code: List[str], template: List[str],
                      code_to_template: List[Optional[int]],
                      template_to_code: List[Optional[int]]):
    """ Match empty lines from template with empty lines from submission basing on already matched non-empty lines. """

    for i in range(len(template)):

        if len(template[i]) == 0:
            left = i
            right = i

            # searching for farthest not matched line from left
            while left >= 0 and template_to_code[left] is None:
                left -= 1

            # searching for farthest not matched line from right
            while right < len(template) and template_to_code[right] is None:
                right += 1

            left = 0 if left < 0 else template_to_code[left] + 1
            right = len(code) if right >= len(template) else template_to_code[right]

            for j in range(left, right):
                if len(code[j]) == 0:
                    code_to_template[j] = i
                    template_to_code[i] = j
                    break


def match_code_with_template(code_lines: List[str], template_lines: List[str], equal: Callable[[str, str], bool]) \
        -> Tuple[List[Optional[int]], List[Optional[int]]]:
    """
    Match code with template and return list of matched indices.

    Example: list of indices [0, 1, None, None, 2] means that the first and the second lines of the submission were
    matched with the first and the second lines of the template accordingly, the third and the forth lines were
    not matched with the template, the fifth line was matched with the third line of the template.
    """
    code_to_template = [None for _ in range(len(code_lines))]
    template_to_code = [None for _ in range(len(template_lines))]
    prev_matched_line = -1

    for i in range(len(template_lines)):
        if len(template_lines[i]) == 0:
            continue
        for j in range(prev_matched_line + 1, len(code_lines)):
            if equal(code_lines[j], template_lines[i]):
                code_to_template[j] = i
                template_to_code[i] = j
                prev_matched_line = j
                break

    match_empty_lines(code_lines, template_lines, code_to_template, template_to_code)

    return code_to_template, template_to_code
