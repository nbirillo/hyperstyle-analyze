from typing import Callable, List, Tuple


def has_comments(line: str) -> bool:
    return '//' in line or '/*' in line


def edit_distance(s1: str, s2: str) -> int:
    """
    Compute edit distance for strings s1 and s2.
    """
    dp = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s2) + 1)]
    for i in range(1, len(s1) + 1):
        dp[0][i] = i
    for i in range(1, len(s2) + 1):
        dp[i][0] = i

    for i in range(1, len(s2) + 1):
        for j in range(1, len(s1) + 1):
            if s1[j - 1] == s2[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1

    return dp[len(s2)][len(s1)]


def equal_charbychar(submission_line: str, template_line: str) -> bool:
    """
    Consider two lines are equal if they are equal char by char.
    """
    return submission_line == template_line


def equal_editdistance(submission_line: str, template_line: str, upper_bound: int = 3) -> bool:
    """
    Consider two strings as equal if their edit distance is no more than upper_bound.
    """
    return edit_distance(submission_line, template_line) <= upper_bound


EQUAL = {
    'char_by_char': equal_charbychar,
    'edit_distance': equal_editdistance,
}


def template2blocks(template: List[str]) -> List[Tuple[int, int, bool]]:
    """
    Build list of blocks (l_ind, r_ind, templ) for template where block [l_ind, r_ind)
    is not supposed to be changed by users if templ = True.
    """
    blocks = []
    block_start = 0
    for i in range(len(template)):
        if has_comments(template[i]):
            if i > 0:
                if not has_comments(template[i - 1]):
                    blocks.append((block_start, i, True))
                    blocks.append((i, i + 1, False))
                else:
                    s, _, _ = blocks[-1]
                    blocks[-1] = (s, i + 1, False)
            block_start = i + 1
    if not has_comments(template[-1]):
        blocks.append((block_start, len(template), True))

    return blocks


def match_empty_lines(submission: List[str], template: List[str],
                      pos_in_template: List[int], pos_in_submission: List[int]) -> List[int]:
    """
    Match empty lines from template with empty lines from submission basing on already matched non-empty lines.
    """

    def get_ind(search_range):
        ind = None
        for i in search_range:
            if pos_in_submission[i] != -1:
                ind = i
                break
        return ind

    def update(j, indl, indr):
        l = pos_in_submission[indl] + 1 if indl is not None else 0
        r = pos_in_submission[indr] if indr is not None else len(submission)
        for i, line in enumerate(submission[l:r]):
            if len(line) == 0:
                pos_in_template[l + i] = j
                break

    for j in range(len(template)):
        if len(template[j]) == 0:
            if j == 0:
                indl = None
                indr = get_ind(range(1, len(template)))
            elif j == len(template) - 1:
                indl = get_ind(range(len(template) - 2, -1, -1))
                indr = None
            else:
                indl = get_ind(range(j - 1, -1, -1))
                indr = get_ind(range(j + 1, len(template)))
            update(j, indl, indr)

    return pos_in_template


def match(submission: List[str], template: List[str], equal: Callable[[str, str], bool]) -> List[int]:
    """
    Match submission with template and return list of matched indices.

    Example: list of indices [0, 1, -1, -1, 2] means that the first and the second lines of the submission were
    matched with the first and the second lines of the template accordingly, the third and the forth lines were
    not matched with the template, the fifth line was matched with the third line of the template.
    """
    pos_in_template = [-1 for _ in range(len(submission))]
    pos_in_submission = [-1 for _ in range(len(template))]
    prev_matched_line = -1

    for j, template_line in enumerate(template):
        if len(template_line) == 0:
            continue
        for i in range(prev_matched_line + 1, len(submission)):
            if equal(submission[i], template_line):
                pos_in_template[i] = j
                pos_in_submission[j] = i
                prev_matched_line = i
                break

    pos_in_template = match_empty_lines(submission, template, pos_in_template, pos_in_submission)

    return pos_in_template