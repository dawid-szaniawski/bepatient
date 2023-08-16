import pytest
from pytest_mock import MockerFixture

from bepatient.waiter_src.exceptions.waiter_exceptions import WaiterConditionWasNotMet
from bepatient.waiter_src.executor import Executor
from bepatient.waiter_src.waiter import wait_for_executor


class TestWaiter:
    def test_wait_success(self, mocker: MockerFixture):
        mock_executor = mocker.MagicMock(spec=Executor)
        mock_executor.is_condition_met.side_effect = [False, True]
        mock_executor.get_result.return_value = "result"

        wait_for_executor(mock_executor, retries=3, delay=0)

        assert mock_executor.is_condition_met.call_count == 2

    def test_wait_timeout_retries(self, mocker: MockerFixture):
        mock_executor = mocker.MagicMock(spec=Executor)
        mock_executor.is_condition_met.return_value = False
        mock_executor.error_message.return_value = "error message"

        with pytest.raises(WaiterConditionWasNotMet, match="error message"):
            wait_for_executor(mock_executor, retries=3, delay=0)

        assert mock_executor.is_condition_met.call_count == 3
