import logging
from time import sleep

from bepatient.waiter_src.exceptions.waiter_exceptions import WaiterConditionWasNotMet
from bepatient.waiter_src.executor import Executor

log = logging.getLogger(__name__)


def wait_for_executor(
    executor: Executor, retries: int, delay: int, raise_error: bool = True
) -> None:
    """Wait for the given executor to meet its condition.

    Args:
        executor (Executor): The executor to wait for.
        retries (int): The number of times to retry the operation.
        delay (int): The delay in seconds between retries.
        raise_error (bool): raises WaiterConditionWasNotMet

    Raises:
        WaiterConditionWasNotMet: if the condition is not met within the specified
            number of attempts."""
    for attempt in range(retries):
        log.debug(
            "Checking whether the condition has been met. The %s approach", attempt + 1
        )
        if executor.is_condition_met():
            log.debug("Condition met!")
            return
        log.debug("The condition has not been met. Waiting: %s", delay)
        sleep(delay)
    if raise_error:
        raise WaiterConditionWasNotMet(executor.error_message())
