from typing import Any

import pytest

from bepatient.waiter_src import comparators


@pytest.mark.parametrize(
    "comparator,data,expected_value,result",
    [
        ("is_equal", 1, 1, True),
        ("is_equal", 1, 2, False),
        ("is_equal", "abc", "abc", True),
        ("is_equal", "abc", "def", False),
        ("is_equal", [1, 2, 3], [1, 2, 3], True),
        ("is_equal", [1, 2, 3], [1, 2], False),
        ("is_equal", True, True, True),
        ("is_equal", False, True, False),
        ("is_equal", None, None, True),
        ("is_equal", None, "", False),
        ("is_equal", None, True, False),
        ("is_equal", 1, None, False),
        ("is_not_equal", 1, 1, False),
        ("is_not_equal", 1, 2, True),
        ("is_not_equal", "abc", "abc", False),
        ("is_not_equal", "abc", "def", True),
        ("is_not_equal", [1, 2, 3], [1, 2, 3], False),
        ("is_not_equal", [1, 2, 3], [1, 2], True),
        ("is_not_equal", True, True, False),
        ("is_not_equal", False, True, True),
        ("is_not_equal", None, None, False),
        ("is_not_equal", None, "", True),
        ("is_not_equal", None, True, True),
        ("is_greater_than", 1, 2, False),
        ("is_greater_than", 2, 1, True),
        ("is_greater_than", 3.2, 2.0, True),
        ("is_greater_than", 0.3, 2, False),
        ("is_greater_than", [0.3, "str"], 2, False),
        ("is_greater_than", None, 2, False),
        ("is_greater_than", "504", 2, False),
        ("is_lesser_than", 1, 2, True),
        ("is_lesser_than", 2, 1, False),
        ("is_lesser_than", 3.2, 2.0, False),
        ("is_lesser_than", 0.3, 2, True),
        ("is_lesser_than", [0.3, "str"], 2, False),
        ("is_lesser_than", None, 2, False),
        ("is_lesser_than", "504", 2, False),
        ("is_greater_than_or_equal", 1, 1, True),
        ("is_greater_than_or_equal", "TEST", "TEST", True),
        ("is_greater_than_or_equal", 1, 2, False),
        ("is_greater_than_or_equal", 2, 1, True),
        ("is_greater_than_or_equal", 3.2, 2.0, True),
        ("is_greater_than_or_equal", 0.3, 2, False),
        ("is_greater_than_or_equal", [0.3, "str"], 2, False),
        ("is_greater_than_or_equal", None, 2, False),
        ("is_greater_than_or_equal", "504", 2, False),
        ("is_lesser_than_or_equal", 1, 1, True),
        ("is_lesser_than_or_equal", "TEST", "TEST", True),
        ("is_lesser_than_or_equal", 1, 2, True),
        ("is_lesser_than_or_equal", 2, 1, False),
        ("is_lesser_than_or_equal", 3.2, 2.0, False),
        ("is_lesser_than_or_equal", 0.3, 2, True),
        ("is_lesser_than_or_equal", [0.3, "str"], 2, False),
        ("is_lesser_than_or_equal", None, 2, False),
        ("is_lesser_than_or_equal", "504", 2, False),
        ("contain", [1, 2, 3], 1, True),
        ("contain", [1, 2, 3], 4, False),
        ("contain", [1, 2, 3.14], 3.14, True),
        ("contain", "bepatient should see that", "bepatient", True),
        ("contain", "bepatient should see that", "noqa", False),
        ("contain", [None], None, True),
        ("contain", None, "TEST", False),
        ("contain", "504", 3.14, False),
        ("not_contain", [1, 2, 3], 1, False),
        ("not_contain", [1, 2, 3], 4, True),
        ("not_contain", [1, 2, 3.14], 3.14, False),
        ("not_contain", "bepatient should see that", "bepatient", False),
        ("not_contain", "bepatient should see that", "noqa", True),
        ("not_contain", [None], None, False),
        ("not_contain", None, "TEST", False),
        ("not_contain", "504", 3.14, False),
        ("contain_all", [1, 2, 3], (1,), True),
        ("contain_all", [1, 2, 3], (4,), False),
        ("contain_all", [1, 2, 3.14], (3.14,), True),
        ("contain_all", "bepatient should see that", ("bepatient",), True),
        ("contain_all", "bepatient should see that", ("noqa",), False),
        ("contain_all", [None], (None,), True),
        ("contain_all", None, ("TEST",), False),
        ("contain_all", "504", [3.14], False),
        ("contain_any", [1, 2, 3], [1, 4], True),
        ("contain_any", [1, 2, 3, 4.5], [4.5], True),
        ("contain_any", "abcd", ["a", "y"], True),
        ("contain_any", None, ["a", "y"], False),
        ("contain_any", "504", [3.14], False),
        ("have_len_equal", "504", 3, True),
        ("have_len_equal", [1, 2, 3, 4, 5], 5, True),
        ("have_len_equal", (1, 2, 3, 4, 5, 6), 6, True),
        ("have_len_equal", (1, 2, 3, 4, 5, 6), 5, False),
        ("have_len_equal", None, 5, False),
        ("have_len_greater", "504", 2, True),
        ("have_len_greater", "504", 5, False),
        ("have_len_greater", [1, 2, 3, 4, 5], 4, True),
        ("have_len_greater", (1, 2, 3, 4, 5, 6), 5, True),
        ("have_len_greater", (1, 2, 3, 4, 5, 6), 6, False),
        ("have_len_greater", None, 5, False),
        ("have_len_lesser", "504", 4, True),
        ("have_len_lesser", "504", 3, False),
        ("have_len_lesser", [1, 2, 3, 4, 5], 6, True),
        ("have_len_lesser", (1, 2, 3, 4, 5, 6), 7, True),
        ("have_len_lesser", (1, 2, 3, 4, 5, 6), 5, False),
        ("have_len_lesser", None, 5, False),
    ],
)
def test_happy_path(
    comparator: comparators.COMPARATORS, data: Any, expected_value: Any, result: bool
):
    assert getattr(comparators, comparator)(data, expected_value) is result
