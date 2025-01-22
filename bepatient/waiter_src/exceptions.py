class ExecutorIsNotReady(Exception):
    def __init__(self, message: str = "The condition has not yet been checked."):
        super().__init__(message)


class WaiterIsNotReady(Exception):
    def __init__(self, message: str = "Not all required attributes have been set!"):
        super().__init__(message)


class WaiterConditionWasNotMet(Exception):
    pass


class ExceptionConditionNotMet(Exception):
    pass
