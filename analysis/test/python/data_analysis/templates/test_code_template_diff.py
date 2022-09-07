from typing import List, Tuple

import pytest

from analysis.src.python.data_analysis.templates.filter_using_diff import get_template_to_code_diffs

DIFF_TEST_DATA = [
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["a = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [(0, 0, 16), (1, 16, 17), (0, 17, 32)]),
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["A = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [(1, 0, 1), (0, 1, 16), (1, 16, 17), (0, 17, 32)]),
    (["# a = 1"],
     ["a = 1"],
     [(0, 0, 5)]),
    # Lines swap does not work properly
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["b = 2\n", "a = 1\n", "c = 3\n", "print(a, b, c)"],
     [(1, 0, 1), (0, 1, 4), (1, 4, 5), (0, 5, 6), (1, 6, 7),
      (0, 7, 10), (1, 10, 11), (0, 11, 16), (1, 16, 17), (0, 17, 32)])
]


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA)
def test_filter_template_issues_using_diff(template: List[str],
                                           code: List[str],
                                           expected_diffs: List[Tuple[int, int, int]]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs
