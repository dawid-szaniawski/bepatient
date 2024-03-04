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
`StatusCodeChecker`.

For an extensive list of available checkers, refer to:

```python
from bepatient import CHECKERS

print(CHECKERS)
```

---

## Custom checkers

If the default checkers provided with _bepatient_ are not sufficient, you can create
your own `Checker`.

To do this, you need an object that inherits from the `Checker` class:

```python
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable

log = logging.getLogger(__name__)


class Checker(ABC):
    """An abstract class defining the interface for a checker to be used by a Waiter."""

    def __init__(self, comparer: Callable[[Any, Any], bool], expected_value: Any):
        self.comparer = comparer
        self.expected_value = expected_value
        self._prepared_data: Any = None

    def __str__(self) -> str:
        """Textual representation of the Checker object for logging"""
        attrs = self.__dict__.copy()
        del attrs["_prepared_data"]
        attrs["checker"] = self.__class__.__name__
        attrs["comparer"] = self.comparer.__name__

        return (
                " | ".join([f"{k.capitalize()}: {v}" for k, v in sorted(attrs.items())])
                + f" | Data: {self._prepared_data}"
        )

    @abstractmethod
    def prepare_data(self, data: Any, run_uuid: str | None = None) -> Any:
        """Prepare the data from the response for comparison.

        Args:
            data (Response): response containing the data.
            run_uuid (str | None): unique run identifier. Defaults to None.

        Returns:
            Any: Data for comparison."""

    def check(self, data: Any) -> bool:
        """Check if the given data meets a certain condition.

        Args:
            data (Any): The data to be checked.

        Returns:
            bool: True if the condition is met, False otherwise."""
        run_uuid = str(uuid.uuid4())
        log.debug("Check uuid: %s | %s", run_uuid, self)

        self._prepared_data = self.prepare_data(data, run_uuid)
        if self.comparer(self._prepared_data, self.expected_value):
            return True
        log.info(
            "Check uuid: %s | Condition not met | Expected: %s | Data: %s",
            run_uuid,
            self.expected_value,
            self._prepared_data,
        )
        return False
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
    def prepare_data(self, data: Any, run_uuid: str | None = None) -> Any:
        return type(data)

```

---
