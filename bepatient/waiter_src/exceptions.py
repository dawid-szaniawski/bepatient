class BePatientException(Exception):
    pass


class ExecutorIsNotReady(BePatientException):
    """We raise it when user want to use `get_result` or `error_message` methods from
    the `Executor` before checking if the condition has been met."""

    def __init__(self, message: str = "The condition has not yet been checked."):
        super().__init__(message)


class WaiterIsNotReady(BePatientException):
    """Not all required attributes have been set."""


class WaiterConditionWasNotMet(BePatientException):
    """Conditions were not met within the specified number of attempts."""


class ExceptionConditionNotMet(BePatientException):
    """One of the conditions causing the wait for the result to end has not been met."""
