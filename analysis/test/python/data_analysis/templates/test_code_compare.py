from typing import Optional, Union

import pytest

from analysis.src.python.data_analysis.templates.utils.code_compare_utils import CodeComparator

LINES_TEST_DATA = [
    ('abc = 1', 'abc = 1', 'edit_distance', False, False, None, True),
    ('abc =  1', 'abc = 1', 'edit_distance', False, False, 1, True),
    ('abc =   1', 'abc = 1', 'edit_distance', False, False, 1, False),
    ('abc = ddd', 'abc = eee', 'edit_ratio', False, False, 0.5, True),
    ('abc = ddddddddd', 'abc = eee', 'edit_ratio', False, False, 0.5, False),
    ('x = 123', 'x = // your code here', 'substring', True, False, None, True),
    ('x = 123', 'x = # your code here', 'substring', True, False, None, True),
    ('x = 123 # your code here', 'x = # your code here', 'substring', True, False, None, True),
    ('x = 123', 'x = /* put your code here */', 'substring', True, False, None, True),
    ('x = /* your code here */ 123', 'x = /* your code here */', 'substring', True, False, None, True),
    ('x = 123 /* your code here */ ', 'x = /* your code here */', 'substring', True, False, None, True),
    ('x = 123 /* your code here */ ', 'y = /* your code here */', 'substring', True, False, None, False),
]


@pytest.mark.parametrize(
    ('code_line', 'template_line', 'equal_type',
     'ignore_trailing_comments', 'ignore_trailing_whitespaces', 'equal_upper_bound', 'result'),
    LINES_TEST_DATA,
)
def test_template_matching(code_line: str,
                           template_line: str,
                           equal_type: str,
                           ignore_trailing_comments: bool,
                           ignore_trailing_whitespaces: bool,
                           equal_upper_bound: Optional[Union[int, float]],
                           result: bool):

    code_comparator = CodeComparator(equal_type, ignore_trailing_comments,
                                     ignore_trailing_whitespaces, equal_upper_bound)

    assert code_comparator.is_equal(code_line, template_line) == result
