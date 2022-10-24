from typing import List, Tuple

import pytest

from analysis.src.python.data_analysis.templates.filter_using_diff import get_template_to_code_diffs, DiffResult, \
    DiffTag

DIFF_TEST_DATA = [
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["a = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [
         DiffResult(DiffTag.EQUAL.value, 0, 16),
         DiffResult(DiffTag.ADDITION.value, 16, 17),
         DiffResult(DiffTag.EQUAL.value, 17, 32)]),
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["A = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [
         DiffResult(DiffTag.ADDITION.value, 0, 1),
         DiffResult(DiffTag.EQUAL.value, 1, 16),
         DiffResult(DiffTag.ADDITION.value, 16, 17),
         DiffResult(DiffTag.EQUAL.value, 17, 32)]),
    (["# a = 1"],
     ["a = 1"],
     [DiffResult(DiffTag.EQUAL.value, 0, 5)]),
    # Lines swap does not work properly
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["b = 2\n", "a = 1\n", "c = 3\n", "print(a, b, c)"],
     [
         DiffResult(DiffTag.ADDITION.value, 0, 1),
         DiffResult(DiffTag.EQUAL.value, 1, 4),
         DiffResult(DiffTag.ADDITION.value, 4, 5),
         DiffResult(DiffTag.EQUAL.value, 5, 6),
         DiffResult(DiffTag.ADDITION.value, 6, 7),
         DiffResult(DiffTag.EQUAL.value, 7, 10),
         DiffResult(DiffTag.ADDITION.value, 10, 11),
         DiffResult(DiffTag.EQUAL.value, 11, 16),
         DiffResult(DiffTag.ADDITION.value, 16, 17),
         DiffResult(DiffTag.EQUAL.value, 17, 32)]),
]


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA)
def test_filter_template_issues_using_diff(template: List[str],
                                           code: List[str],
                                           expected_diffs: List[DiffResult]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs
