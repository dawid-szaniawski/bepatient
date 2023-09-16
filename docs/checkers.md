# Checkers
## Default checkers

When working with bepatient, you'll find that each checking object should inherit from
the `Checker` class or one of its derived classes.
At the moment, _bepatient_ exclusively supports response checkers:

```yaml
checkers:
  - json_checker
  - headers_checker
```

Furthermore, it's important to note that `RequestsExecutor` requires the `status_code`
attribute. This is because, prior to evaluating other checkers, it employs the
`StatusCodeChecker`, a subclass of `ResponseChecker`.

For an extensive list of available checkers, refer to:

```python
from bepatient import CHECKERS


print(CHECKERS)
```

---

## Custom checkers

If the default checkers provided with _bepatient_ are not sufficient, you can create
your own Checker.

To do this, you need an object that inherits from the Checker class:

```python
from abc import ABC, abstractmethod
from typing import Any


class Checker(ABC):
    """An abstract class defining the interface for a checker to be used by a Waiter."""

    @abstractmethod
    def __str__(self) -> str:
        """Textual representation of the Checker object for logging"""

    @abstractmethod
    def check(self, data: Any) -> bool:
        """Check if the given data meets a certain condition.

        Args:
            data (Any): The data to be checked.

        Returns:
            bool: True if the condition is met, False otherwise."""
```

The `__str__` method makes it easier for us to analyze any potential reasons why the
condition was not met. Therefore, it should provide information about what the checker
is verifying and what conditions need to be met.

The `check` method should perform all the necessary operations to check whether the
condition has been met and return `True` if the condition has been met and `False` if
it has not.

Example:

```python
from typing import Any

from bepatient import Checker


class IsListChecker(Checker):
    def __init__(self):
        self.data = None

    def __str__(self):
        return f"{self.__class__.__name__} | {self.data}"

    def check(self, data: Any) -> bool:
        self.data = data
        return isinstance(data, list)

```

---
