from typing import List, Optional, Union

import pytest

from analysis.src.python.data_analysis.templates.template_matching import match_code_with_template
from analysis.src.python.data_analysis.templates.utils.code_compare_utils import CodeComparator


def array_equal(actual_array: List[Optional[int]], expected_array: List[Optional[int]]):
    return len(actual_array) == len(expected_array) and \
           all([(actual_x is None and expected_x is None) or actual_x == expected_x
                for actual_x, expected_x in zip(actual_array, expected_array)])


TEMPLATE_TEST_DATA = [
    # char by char testing
    (['a', 'b'], ['a', 'b'], 'edit_distance', False, False, 0, [0, 1], [0, 1]),
    (['a', 'b', 'c'], ['a', 'b'], 'edit_distance', False, False, 0, [0, 1, None], [0, 1]),
    (['c', 'a', 'b'], ['a', 'b'], 'edit_distance', False, False, 0, [None, 0, 1], [1, 2]),
    (['a', 'c', 'b'], ['a', 'b'], 'edit_distance', False, False, 0, [0, None, 1], [0, 2]),
    (['a', '', 'b'], ['a', '', 'b'], 'edit_distance', False, False, 0, [0, 1, 2], [0, 1, 2]),
    (['', 'a', '', 'b'], ['a', '', 'b'], 'edit_distance', False, False, 0, [None, 0, 1, 2], [1, 2, 3]),
    (['', 'a', '', 'b'], ['', 'a', 'b'], 'edit_distance', False, False, 0, [0, 1, None, 2], [0, 1, 3]),
    (['', '', 'a', '', 'b', ''], ['', 'a', '', 'b', ''],
     'edit_distance', False, False, 0,
     [0, None, 1, 2, 3, 4], [0, 2, 3, 4, 5]),
    (['a', 'b', '', '', 'c', 'd', 'e', '', '', 'f'], ['a', 'b', '', '', 'f'],
     'edit_distance', False, False, 0,
     [0, 1, 2, 3, None, None, None, None, None, 4], [0, 1, 2, 3, 9]),
    (['', 'a', 'b', '', '', 'c', 'd', '', 'e', '', '', 'f', ''], ['', '', 'a', 'b', '', '', 'f', ''],
     'edit_distance', False, False, 0,
     [0, 2, 3, 4, 5, None, None, None, None, None, None, 6, 7], [0, None, 1, 2, 3, 4, 11, 12]),

    #  test matching with substring equal
    (['x = 1', 'y = 2'], ['// program', 'x = ', 'y = '],
     'substring', False, False, None, [1, 2], [None, 0, 1]),
    (['', 'x = 1', 'y = 2', 'z = 3', ''], ['x = // your code here', 'y = // your code here', 'z = 3'],
     'substring', True, False, None, [None, 0, 1, 2, None], [1, 2, 3]),

    #  test matching with substring edit_distance or edit_ration with not zero change
    (['x = 1', 'y = 3', ''], ['x = 1', 'y = 2', 'z = 3'],
     'edit_distance', False, False, 1, [0, 1, None], [0, 1, None]),
    (['x = 3', 'z = 2'], ['x = 1', 'y = 2', ''],
     'edit_distance', False, False, 2, [0, 1], [0, 1, None]),
    (['x = 123'], ['x = '], 'edit_ratio', False, False, 0.5, [0], [0]),

    #  test matching with trailing spaces ignored
    (['\t\tx = 1234 ', ''], ['x = 1234'], 'edit_distance', False, True, 0, [0, None], [0]),
]


@pytest.mark.parametrize(
    ('code', 'template', 'equal_type', 'ignore_trailing_comments', 'ignore_trailing_whitespaces', 'equal_upper_bound',
     'code_to_template', 'template_to_code'),
    TEMPLATE_TEST_DATA,
)
def test_template_matching(code: List[str],
                           template: List[str],
                           equal_type: str,
                           ignore_trailing_comments: bool,
                           ignore_trailing_whitespaces: bool,
                           equal_upper_bound: Optional[Union[int, float]],
                           code_to_template: List[Optional[int]],
                           template_to_code: List[Optional[int]]):
    code_comparator = CodeComparator(equal_type, ignore_trailing_comments,
                                     ignore_trailing_whitespaces, equal_upper_bound)
    actual_code_to_template, actual_template_to_code = \
        match_code_with_template(code, template, code_comparator.is_equal, code_comparator.is_empty)

    assert array_equal(actual_code_to_template, code_to_template)
    assert array_equal(actual_template_to_code, template_to_code)
