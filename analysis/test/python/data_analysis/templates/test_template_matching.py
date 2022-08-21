from typing import Callable, List, Optional

import pytest

from analysis.src.python.data_analysis.templates.template_matching import equal_char_by_char, match_code_with_template


def array_equal(actual_array: List[Optional[int]], expected_array: List[Optional[int]]):
    return len(actual_array) == len(expected_array) and \
           all([(actual_x is None and expected_x is None) or actual_x == expected_x
                for actual_x, expected_x in zip(actual_array, expected_array)])


TEMPLATE_TEST_DATA = [
    (['a', 'b'], ['a', 'b'], equal_char_by_char, [0, 1], [0, 1]),
    (['a', 'b', 'c'], ['a', 'b'], equal_char_by_char, [0, 1, None], [0, 1]),
    (['c', 'a', 'b'], ['a', 'b'], equal_char_by_char, [None, 0, 1], [1, 2]),
    (['a', 'c', 'b'], ['a', 'b'], equal_char_by_char, [0, None, 1], [0, 2]),
    (['a', '', 'b'], ['a', '', 'b'], equal_char_by_char, [0, 1, 2], [0, 1, 2]),
    (['', 'a', '', 'b'], ['a', '', 'b'], equal_char_by_char, [None, 0, 1, 2], [1, 2, 3]),
    (['', 'a', '', 'b'], ['', 'a', 'b'], equal_char_by_char, [0, 1, None, 2], [0, 1, 3]),
    (['', '', 'a', '', 'b', ''], ['', 'a', '', 'b', ''], equal_char_by_char, [0, None, 1, 2, 3, 4], [0, 2, 3, 4, 5]),
    (['a', 'b', '', '', 'c', 'd', 'e', '', '', 'f'], ['a', 'b', '', '', 'f'],
     equal_char_by_char,
     [0, 1, 2, 3, None, None, None, None, None, 4], [0, 1, 2, 3, 9]),
    (['', 'a', 'b', '', '', 'c', 'd', '', 'e', '', '', 'f', ''], ['', '', 'a', 'b', '', '', 'f', ''],
     equal_char_by_char,
     [0, 2, 3, 4, 5, None, None, None, None, None, None, 6, 7], [0, None, 1, 2, 3, 4, 11, 12]),
]


@pytest.mark.parametrize(
    ('code', 'template', 'equal', 'code_to_template', 'template_to_code'),
    TEMPLATE_TEST_DATA,
)
def test_template_matching(code: List[str],
                           template: List[str],
                           equal: Callable[[str, str], bool],
                           code_to_template: List[Optional[int]],
                           template_to_code: List[Optional[int]]):
    actual_code_to_template, actual_template_to_code = match_code_with_template(code, template, equal)

    assert array_equal(actual_code_to_template, code_to_template)
    assert array_equal(actual_template_to_code, template_to_code)
