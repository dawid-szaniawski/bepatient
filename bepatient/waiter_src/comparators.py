from collections.abc import Iterable, Sized
from typing import Any, Literal


def is_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is equal to expected_value, False otherwise."""
    return data == expected_value


def is_not_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is not equal to expected_value, False otherwise."""
    return data != expected_value


def is_greater_than(data: Any, expected_value: Any) -> bool:
    """Returns True if data is greater than expected_value, False otherwise."""
    try:
        return data > expected_value
    except TypeError:
        return False


def is_lesser_than(data: Any, expected_value: Any) -> bool:
    """Returns True if data is lesser than expected_value, False otherwise."""
    try:
        return data < expected_value
    except TypeError:
        return False


def is_greater_than_or_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is greater than or equal to expected_value,
    False otherwise."""
    try:
        return data >= expected_value
    except TypeError:
        return False


def is_lesser_than_or_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is lesser than or equal to expected_value,
    False otherwise."""
    try:
        return data <= expected_value
    except TypeError:
        return False


def contain(data: Iterable[Any], expected_value: Any) -> bool:
    """Returns True if expected_value is present in data, False otherwise."""
    try:
        return expected_value in data
    except TypeError:
        return False


def not_contain(data: Iterable[Any], expected_value: Any) -> bool:
    """Returns True if expected_value is not present in data, False otherwise."""
    try:
        return expected_value not in data
    except TypeError:
        return False


def contain_all(data: Iterable[Any], expected_value: Iterable[Any]) -> bool:
    """Returns True if all elements in expected_value are present in data,
    False otherwise."""
    try:
        return all((i in data for i in expected_value))
    except TypeError:
        return False


def contain_any(data: Iterable[Any], expected_value: Iterable[Any]) -> bool:
    """Returns True if any element in expected_value is present in data,
    False otherwise."""
    try:
        return any((i in data for i in expected_value))
    except TypeError:
        return False


def have_len_equal(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is equal to expected_value,
    False otherwise."""
    try:
        return len(data) == expected_value
    except TypeError:
        return False


def have_len_greater(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is greater than expected_value,
    False otherwise."""
    try:
        return len(data) > expected_value
    except TypeError:
        return False


def have_len_lesser(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is lesser than expected_value,
    False otherwise."""
    try:
        return len(data) < expected_value
    except TypeError:
        return False


COMPARATORS = Literal[
    "is_equal",
    "is_not_equal",
    "is_greater_than",
    "is_lesser_than",
    "is_greater_than_or_equal",
    "is_lesser_than_or_equal",
    "contain",
    "not_contain",
    "contain_all",
    "contain_any",
    "have_len_equal",
    "have_len_greater",
    "have_len_lesser",
]
