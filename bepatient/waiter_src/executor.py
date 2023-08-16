from abc import ABC, abstractmethod
from typing import Any


class Executor(ABC):
    """An abstract base class for defining an executor that can be waited for."""

    @abstractmethod
    def is_condition_met(self) -> bool:
        """Check whether the condition has been met.

        Returns:
            bool: True if the condition has been met, False otherwise."""
        ...

    @abstractmethod
    def get_result(self) -> Any:
        """Returns the result of performed actions."""
        ...

    @abstractmethod
    def error_message(self) -> str:
        """Return a detailed error message if the condition has not been met."""
        ...
