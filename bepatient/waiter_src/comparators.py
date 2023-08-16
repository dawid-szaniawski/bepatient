from typing import Any, Iterable, Literal, Sized


def is_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is equal to expected_value, False otherwise."""
    return data == expected_value


def is_not_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is not equal to expected_value, False otherwise."""
    return data != expected_value


def is_greater_than(data: Any, expected_value: Any) -> bool:
    """Returns True if data is greater than expected_value, False otherwise."""
    return data > expected_value


def is_lesser_than(data: Any, expected_value: Any) -> bool:
    """Returns True if data is lesser than expected_value, False otherwise."""
    return data < expected_value


def is_greater_than_or_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is greater than or equal to expected_value,
    False otherwise."""
    return data >= expected_value


def is_lesser_than_or_equal(data: Any, expected_value: Any) -> bool:
    """Returns True if data is lesser than or equal to expected_value,
    False otherwise."""
    return data <= expected_value


def contain(data: Iterable[Any], expected_value: Any) -> bool:
    """Returns True if expected_value is present in data, False otherwise."""
    return expected_value in data


def not_contain(data: Iterable[Any], expected_value: Any) -> bool:
    """Returns True if expected_value is not present in data, False otherwise."""
    return expected_value not in data


def contain_all(data: Iterable[Any], expected_value: Iterable[Any]) -> bool:
    """Returns True if all elements in expected_value are present in data,
    False otherwise."""
    return all((i in data for i in expected_value))


def contain_any(data: Iterable[Any], expected_value: Iterable[Any]) -> bool:
    """Returns True if any element in expected_value is present in data,
    False otherwise."""
    return any((i in data for i in expected_value))


def have_len_equal(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is equal to expected_value,
    False otherwise."""
    return len(data) == expected_value


def have_len_greater(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is greater than expected_value,
    False otherwise."""
    return len(data) > expected_value


def have_len_lesser(data: Sized, expected_value: int) -> bool:
    """Returns True if the length of data is lesser than expected_value,
    False otherwise."""
    return len(data) < expected_value


COMP_DICT = {
    "is_equal": is_equal,
    "is_not_equal": is_not_equal,
    "is_greater_than": is_greater_than,
    "is_lesser_than": is_lesser_than,
    "is_greater_than_or_equal": is_greater_than_or_equal,
    "is_lesser_than_or_equal": is_lesser_than_or_equal,
    "contain": contain,
    "not_contain": not_contain,
    "contain_all": contain_all,
    "contain_any": contain_any,
    "have_len_equal": have_len_equal,
    "have_len_greater": have_len_greater,
    "have_len_lesser": have_len_lesser,
}

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
