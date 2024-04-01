from abc import ABC, abstractmethod
from typing import Any

from bepatient.waiter_src.checkers.checker import Checker
from bepatient.waiter_src.exceptions.executor_exceptions import ExecutorIsNotReady


class Executor(ABC):
    """An abstract base class for defining an executor that can be waited for."""

    def __init__(self):
        """Cursor should have cursor_factory that returns dict object"""
        self._checkers: list[Checker] = []
        self._failed_checkers: list[Checker] = []
        self._result: Any = None
        self._input: str | None = None

    def add_checker(self, checker: Checker):
        """Adds checker function to the list of checkers."""
        self._checkers.append(checker)
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
