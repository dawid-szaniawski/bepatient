import logging
from time import sleep
from typing import Any, Callable

from .waiter_src.comparators import Comparator, is_equal
from .waiter_src.exceptions import WaiterConditionWasNotMet

logger = logging.getLogger(__name__)


def retry(
    expected: Any, *, comparer: Comparator = is_equal, loops: int = 60, delay: int = 1
):
    """
    Simple decorator, that retries function if its result is different from expected.

    Example:
        ```python
            @bepatient.retry(200)
            def send_request():
                return requests.get('https://webludus.pl/en').status_code

            result = send_request()
            assert result == 200
        ```
    """

    def wrap(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapped(*args, **kwargs) -> Any:
            for attempt in range(loops):
                logger.info(
                    "Checking whether the condition has been met. The %s approach."
                    " Expected: %s",
                    attempt + 1,
                    expected,
                )
                result = func(*args, **kwargs)
                if comparer(expected, result):
                    logger.info("Condition met! Result: %s", result)
                    return result
                logger.info(
                    "Condition was not met! Expected: %s | Result %s", expected, result
                )
                sleep(delay)
            raise WaiterConditionWasNotMet()

        return wrapped

    return wrap
