from abc import ABC, abstractmethod
from typing import Any

from bepatient.waiter_src.checkers.checker import Checker
from bepatient.waiter_src.conditions_manager import ConditionsManager
from bepatient.waiter_src.exceptions import ExecutorIsNotReady


class Executor(ABC):
    """An abstract base class for defining an executor that can be waited for."""

    def __init__(self):
        self.conditions_manager = ConditionsManager()
        self._failed_checkers: list[Checker] = []
        self._result: Any = None
        self._input: str | None = None

    def add_exception_condition(self, checker: Checker):
        """Adds checker function to the condition's manager. If the checker condition
        is not met, it raises ExceptionConditionNotMet."""
        self.conditions_manager.exception_conditions.append(checker)
        return self

    def add_pre_condition(self, checker: Checker):
        """Adds checker function to the list of pre_conditions - conditions that will
        be checked before the main ones and after those that may result in an error.
        For example, when we want to check the response status code before verifying
        the content of the body."""
        self.conditions_manager.pre_conditions.append(checker)
        return self

    def add_main_condition(self, checker: Checker):
        """Adds checker function to the list of main_conditions in ConditionsManager.
        These are the main conditions to be met. That which we really care about
        checking the most."""
        self.conditions_manager.main_conditions.append(checker)
        return self

    @abstractmethod
    def is_condition_met(self) -> bool:
        """Check whether the condition has been met.

        Returns:
            bool: True if the condition has been met, False otherwise."""

    def get_result(self) -> Any:
        """Returns the result of performed actions."""
        if self._result is not None:
            return self._result
        raise ExecutorIsNotReady()

    def error_message(self) -> str:
        """Return a detailed error message if the condition has not been met."""
        if self._result is not None and len(self._failed_checkers) > 0:
            checkers = ", ".join([str(checker) for checker in self._failed_checkers])
            return (
                "The condition has not been met!"
                f" | Failed checkers: ({checkers})"
                f" | {self._input}"
            )
        if self._result is not None and len(self._failed_checkers) == 0:
            return "All conditions have been met."
        raise ExecutorIsNotReady()
