from typing import Any, Callable

import pytest
from requests import Response

from bepatient.waiter_src.checker import Checker


@pytest.fixture
def checker_true(is_equal_comparer: Callable[[Any, Any], bool]) -> Checker:
    class CheckerMocker(Checker):
        def __str__(self) -> str:
            return "I'm truthy"

        def prepare_data(self, data: Any, run_uuid: str | None = None) -> None:
            """mock"""

        def check(self, data: Any) -> bool:
            return True

    checker = CheckerMocker(comparer=is_equal_comparer, expected_value="")
    assert str(checker) == "I'm truthy"
    return checker


@pytest.fixture
def checker_false(is_equal_comparer: Callable[[Any, Any], bool]) -> Checker:
    class CheckerMocker(Checker):
        def __str__(self) -> str:
            return "I'm falsy"

        def prepare_data(self, data: Any, run_uuid: str | None = None) -> None:
            """mock"""

        def check(self, data: Any) -> bool:
            return False

    return CheckerMocker(comparer=is_equal_comparer, expected_value="")


@pytest.fixture
def response_without_cookies_in_request(example_response: Response) -> Response:
    del example_response.request.headers["Cookie"]
    return example_response
