import logging
from typing import Any, Literal

from bepatient.waiter_src.checkers.checker import Checker
from bepatient.waiter_src.exceptions import ExceptionConditionNotMet

log = logging.getLogger(__name__)
CONDITION_LEVEL = Literal["exception", "pre", "main"]  # pylint: disable=invalid-name


class ConditionsManager:
    """Manages and evaluates conditions grouped into three levels:
    - exception_conditions - conditions that trigger an exception if not met,
    - precondition_conditions - conditions that are checked prior to the main
        conditions,
    - main_conditions - core conditions, those are checked last."""

    def __init__(self):
        self.exception_conditions = []
        self.pre_conditions = []
        self.main_conditions = []

    def check_all(self, result: Any, check_uuid: str) -> list[Checker]:
        """Simply checks all defined conditions."""
        if not self.main_conditions:
            log.info("No main conditions available")

        if self.exception_conditions:
            failed_checkers = [
                checker
                for checker in self.exception_conditions
                if not checker.check(result, check_uuid)
            ]
            if failed_checkers:
                checkers = ", ".join((str(checker) for checker in failed_checkers))
                raise ExceptionConditionNotMet(f"Failed checkers: {checkers}")

        if self.pre_conditions:
            failed_checkers = [
                checker
                for checker in self.pre_conditions
                if not checker.check(result, check_uuid)
            ]
            if failed_checkers:
                return failed_checkers
        return [
            checker
            for checker in self.main_conditions
            if not checker.check(result, check_uuid)
        ]
