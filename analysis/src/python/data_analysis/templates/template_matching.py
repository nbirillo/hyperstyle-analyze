from typing import Callable, List, Optional, Tuple


def match_empty_lines(code: List[str], template: List[str],
                      code_to_template: List[Optional[int]],
                      template_to_code: List[Optional[int]],
                      is_empty: Callable[[str], bool]):
    """ Match empty lines from template with empty lines from submission basing on already matched non-empty lines. """

    for i in range(len(template)):
        if template_to_code[i] is not None:
            continue

        if is_empty(template[i]):
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
                if is_empty(code[j]) and code_to_template[j] is None:
                    code_to_template[j] = i
                    template_to_code[i] = j
                    break


def match_code_lines(code_lines: List[str], template_lines: List[str],
                     code_to_template: List[Optional[int]],
                     template_to_code: List[Optional[int]],
                     is_equal: Callable[[str, str], bool],
                     is_empty: Callable[[str], bool]):
    """ Match code with template not empty lines. """

    prev_matched_line = -1

    for i in range(len(template_lines)):
        if is_empty(template_lines[i]) or template_to_code[i] is not None:
            continue
        for j in range(prev_matched_line + 1, len(code_lines)):
            if is_equal(code_lines[j], template_lines[i]) and code_to_template[j] is None:
                code_to_template[j] = i
                template_to_code[i] = j
                prev_matched_line = j
                break


def match_code_with_template(code_lines: List[str], template_lines: List[str],
                             is_equal: Callable[[str, str], bool],
                             is_empty: Callable[[str], bool]) \
        -> Tuple[List[Optional[int]], List[Optional[int]]]:
    """
    Match code with template and return list of matched indices.

    Example: list of indices [0, 1, None, None, 2] means that the first and the second lines of the submission were
    matched with the first and the second lines of the template accordingly, the third and the forth lines were
    not matched with the template, the fifth line was matched with the third line of the template.
    """

    code_to_template = [None for _ in range(len(code_lines))]
    template_to_code = [None for _ in range(len(template_lines))]
    match_code_lines(code_lines, template_lines, code_to_template, template_to_code, is_equal, is_empty)
    match_empty_lines(code_lines, template_lines, code_to_template, template_to_code, is_empty)

    return code_to_template, template_to_code
