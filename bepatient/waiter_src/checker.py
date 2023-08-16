from abc import ABC, abstractmethod
from typing import Any


class Checker(ABC):
    """An abstract class defining the interface for a checker to be used by a Waiter."""

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def check(self, data: Any) -> bool:
        """Check if the given data meets a certain condition.

        Args:
            data (Any): The data to be checked.

        Returns:
            bool: True if the condition is met, False otherwise."""
        ...
