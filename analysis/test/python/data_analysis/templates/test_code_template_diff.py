from typing import List

import pytest

from analysis.src.python.data_analysis.templates.filter_by_diff import DiffInterval, DiffResult, DiffTag, \
    get_template_to_code_diffs

DIFF_TEST_DATA = [
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["a = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [
         DiffResult(DiffTag.EQUAL.value, "a = 1\nb = 2\nc = ", DiffInterval(0, 16), DiffInterval(0, 16)),
         DiffResult(DiffTag.DELETION.value, "# put your code here", DiffInterval(16, 36), DiffInterval(16, 16)),
         DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(36, 36), DiffInterval(16, 17)),
         DiffResult(DiffTag.EQUAL.value, "\nprint(a, b, c)", DiffInterval(36, 51), DiffInterval(17, 32))]),
    (["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
     ["A = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
     [
         DiffResult(DiffTag.DELETION.value, "a", DiffInterval(0, 1), DiffInterval(0, 0)),
         DiffResult(DiffTag.ADDITION.value, "A", DiffInterval(1, 1), DiffInterval(0, 1)),
         DiffResult(DiffTag.EQUAL.value, " = 1\nb = 2\nc = ", DiffInterval(1, 16), DiffInterval(1, 16)),
         DiffResult(DiffTag.DELETION.value, "# put your code here", DiffInterval(16, 36), DiffInterval(16, 16)),
         DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(36, 36), DiffInterval(16, 17)),
         DiffResult(DiffTag.EQUAL.value, "\nprint(a, b, c)", DiffInterval(36, 51), DiffInterval(17, 32))]),
    (["# a = 1"],
     ["a = 1"],
     [
         DiffResult(DiffTag.DELETION.value, "# ", DiffInterval(0, 2), DiffInterval(0, 0)),
         DiffResult(DiffTag.EQUAL.value, "a = 1", DiffInterval(2, 7), DiffInterval(0, 5))]),
    # Lines swap does not work properly
    (["a = 1\n", "b = 2\n", "c = 3\n"],
     ["b = 2\n", "a = 1\n", "c = 3\n"],
     [
         DiffResult(DiffTag.DELETION.value, "a", DiffInterval(0, 1), DiffInterval(0, 0)),
         DiffResult(DiffTag.ADDITION.value, "b", DiffInterval(1, 1), DiffInterval(0, 1)),
         DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(1, 4), DiffInterval(1, 4)),

         DiffResult(DiffTag.DELETION.value, "1", DiffInterval(4, 5), DiffInterval(4, 4)),
         DiffResult(DiffTag.ADDITION.value, "2", DiffInterval(5, 5), DiffInterval(4, 5)),
         DiffResult(DiffTag.EQUAL.value, "\n", DiffInterval(5, 6), DiffInterval(5, 6)),

         DiffResult(DiffTag.DELETION.value, "b", DiffInterval(6, 7), DiffInterval(6, 6)),
         DiffResult(DiffTag.ADDITION.value, "a", DiffInterval(7, 7), DiffInterval(6, 7)),
         DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(7, 10), DiffInterval(7, 10)),

         DiffResult(DiffTag.DELETION.value, "2", DiffInterval(10, 11), DiffInterval(10, 10)),
         DiffResult(DiffTag.ADDITION.value, "1", DiffInterval(11, 11), DiffInterval(10, 11)),
         DiffResult(DiffTag.EQUAL.value, "\nc = 3\n", DiffInterval(11, 18), DiffInterval(11, 18))]),
]


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA)
def test_filter_template_issues_using_diff(template: List[str],
                                           code: List[str],
                                           expected_diffs: List[DiffResult]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs
