from typing import Any

import pytest
import requests
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture

from bepatient import retry
from bepatient.waiter_src.comparators import Comparator
from bepatient.waiter_src.exceptions import WaiterConditionWasNotMet


class TestRetry:
    def test_default_comparator(self, caplog: LogCaptureFixture):
        @retry(1)
        def simple_function():
            return 1

        assert simple_function() == 1
        logs = [
            (
                "bepatient.retry",
                20,
                "Checking whether the condition has been met. The 1 approach."
                " Expected: 1",
            ),
            ("bepatient.retry", 20, "Condition met! Result: 1"),
        ]
        assert caplog.record_tuples == logs

    def test_raise_error(self, caplog: LogCaptureFixture):
        @retry("TEST", loops=1, delay=0)
        def simple_function():
            return 1

        with pytest.raises(WaiterConditionWasNotMet):
            simple_function()
        logs = [
            (
                "bepatient.retry",
                20,
                "Checking whether the condition has been met. The 1 approach."
                " Expected: TEST",
            ),
            ("bepatient.retry", 20, "Condition was not met! Expected: TEST | Result 1"),
        ]
        assert caplog.record_tuples == logs

    @pytest.mark.parametrize(
        "comparator,expected",
        [(lambda a, b: a == b, 200), (lambda a, b: b in a, [201, 200])],
    )
    def test_wait_for_expected(
        self, comparator: Comparator, expected: Any, mocker: MockerFixture
    ):
        @retry(expected=expected, comparer=comparator, delay=0)
        def simple_function() -> int | None:
            try:
                return requests.get("https://webludus.pl", timeout=1).status_code
            except AssertionError:
                return None

        res1 = requests.Response()
        res1.status_code = 404
        res2 = requests.Response()
        res2.status_code = 200

        mocker.patch("requests.get", side_effect=[AssertionError(), res1, res2])
        assert simple_function() == 200
