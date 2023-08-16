class ExecutorIsNotReady(Exception):
    def __init__(self, message: str = "The condition has not yet been checked."):
        super().__init__(message)
