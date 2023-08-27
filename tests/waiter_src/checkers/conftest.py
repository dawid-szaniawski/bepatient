from typing import Callable, Any

from pytest import fixture


@fixture
def is_equal() -> Callable[[Any, Any], bool]:
    return lambda a, b: a == b
