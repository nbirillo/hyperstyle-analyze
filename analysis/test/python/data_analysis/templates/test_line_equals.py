from typing import Callable

import pytest

from analysis.src.python.data_analysis.templates.utils.code_compare_utils import equal_char_by_char, \
    equal_edit_distance, equal_edit_ratio, equal_substring

LINES_TEST_DATA = [
    ('abc = 1', 'abc = 1', equal_char_by_char, True),
    ('abc =  1', 'abc = 1', lambda s1, s2: equal_edit_distance(s1, s2, 1), True),
    ('abc =   1', 'abc = 1', lambda s1, s2: equal_edit_distance(s1, s2, 1), False),
    ('abc = ddd', 'abc = eee', lambda s1, s2: equal_edit_ratio(s1, s2, 0.5), True),
    ('abc = ddddddddd', 'abc = eee', lambda s1, s2: equal_edit_ratio(s1, s2, 0.5), False),
    ('x = 123', 'x = // your code here', equal_substring, True),
    ('x = 123', 'x = # your code here', equal_substring, True),
    ('x = 123 # your code here', 'x = # your code here', equal_substring, True),
    ('x = 123', 'x = /* put your code here */', equal_substring, True),
    ('x = /* your code here */ 123', 'x = /* your code here */', equal_substring, True),
    ('x = 123 /* your code here */ ', 'x = /* your code here */', equal_substring, True),
    ('x = 123 /* your code here */ ', 'y = /* your code here */', equal_substring, False),
]


@pytest.mark.parametrize(
    ('code_line', 'template_line', 'equal', 'result'),
    LINES_TEST_DATA,
)
def test_template_matching(code_line: str,
                           template_line: str,
                           equal: Callable[[str, str], bool],
                           result: bool):
    assert equal(code_line, template_line) == result
