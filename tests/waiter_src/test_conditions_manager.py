import pytest
from _pytest.logging import LogCaptureFixture

from bepatient import Checker
from bepatient.waiter_src.conditions_manager import ConditionsManager
from bepatient.waiter_src.exceptions import ExceptionConditionNotMet


class TestConditionsManager:
    def test_exception_condition_raise_exception_if_not_met(
        self, checker_false: Checker, caplog: LogCaptureFixture
    ):
        manager = ConditionsManager()
        manager.exception_conditions.append(checker_false)

        msg = (
            "Failed checkers: Checker: CheckerMocker | Comparer: comparer"
            " | Expected_value: TEST | Data: Ok"
        )
        with pytest.raises(ExceptionConditionNotMet, match=msg):
            manager.check_all("RESULT", "UUID")

        assert caplog.record_tuples == [
            (
                "bepatient.waiter_src.conditions_manager",
                20,
                "No main conditions available",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: UUID | Checker: CheckerMocker | Comparer: comparer"
                " | Expected_value: TEST | Data: Ok",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check uuid: UUID | Condition not met | Checker: CheckerMocker"
                " | Comparer: comparer | Expected_value: TEST | Data: Ok",
            ),
        ]

    def test_pre_conditions(self, checker_true: Checker, checker_false: Checker):
        manager = ConditionsManager()
        manager.main_conditions.append(checker_true)
        manager.exception_conditions.append(checker_true)
        manager.pre_conditions.append(checker_false)

        result = manager.check_all("RESULT", "UUID")

        assert result == [checker_false]

    def test_main_conditions(self, checker_true: Checker, checker_false: Checker):
        manager = ConditionsManager()
        manager.main_conditions.append(checker_false)
        manager.exception_conditions.append(checker_true)
        manager.pre_conditions.append(checker_true)

        result = manager.check_all("RESULT", "UUID")

        assert result == [checker_false]
