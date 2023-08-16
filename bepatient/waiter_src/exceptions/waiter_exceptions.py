class WaiterIsNotReady(Exception):
    def __init__(self, message: str = "Not all required attributes have been set!"):
        super().__init__(message)


class WaiterConditionWasNotMet(Exception):
    pass
