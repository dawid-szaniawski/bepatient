import logging

from requests import PreparedRequest, Response, Session
from requests.exceptions import RequestException

from bepatient.curler import Curler
from bepatient.waiter_src.checker import Checker
from bepatient.waiter_src.checkers.response_checkers import StatusCodeChecker
from bepatient.waiter_src.comparators import is_equal
from bepatient.waiter_src.exceptions.executor_exceptions import ExecutorIsNotReady
from bepatient.waiter_src.executor import Executor

log = logging.getLogger(__name__)


class RequestsExecutor(Executor):
    """An executor that sends a request and waits for a certain condition to be met.
    Args:
        req_or_res (PreparedRequest): The request to send.
        session (Session): The requests session to use."""

    def __init__(
        self,
        req_or_res: PreparedRequest | Response,
        expected_status_code: int,
        session: Session | None = None,
    ):
        self._status_code_checker = StatusCodeChecker(is_equal, expected_status_code)
        self._checkers: list[Checker] = []
        self._failed_checkers: list[Checker] = []
        self._response: Response | None = None

        if session:
            self.session = session
        else:
            log.info("Creating new Session object")
            self.session = Session()

        if isinstance(req_or_res, Response):
            self.session.headers.update(req_or_res.request.headers)
            self._response = req_or_res
            if len(req_or_res.history) > 0:
                self.request = req_or_res.history[0].request
            else:
                self.request = req_or_res.request
        else:
            self.request = req_or_res

    def add_checker(self, checker: Checker):
        """Adds checker function to the list of checkers."""
        self._checkers.append(checker)
        return self

    def is_condition_met(self) -> bool:
        """Sends the request and check if all checkers pass or timeout occurs.

        Returns:
            bool: True if all checkers pass, False otherwise.

        Raises:
            ExecutorIsNotReady: If the executor is not ready to send the request."""
        try:
            self._response = self.session.send(self.request)
        except RequestException:
            log.exception("RequestException! CURL: %s", Curler().to_curl(self.request))
            return False

        if self._status_code_checker.check(self._response):
            self._failed_checkers = [
                checker
                for checker in self._checkers
                if not checker.check(self._response)
            ]
        else:
            self._failed_checkers = [self._status_code_checker]

        if len(self._failed_checkers) == 0:
            return True
        return False

    def get_result(self) -> Response:
        """Returns the response received from the server."""
        if self._response is not None:
            return self._response
        raise ExecutorIsNotReady()

    def error_message(self) -> str:
        """Return a detailed error message if the condition has not been met."""
        if self._response is not None and len(self._failed_checkers) > 0:
            checkers = ", ".join([str(checker) for checker in self._failed_checkers])
            return (
                "The condition has not been met!"
                f" | Failed checkers: ({checkers})"
                f" | {Curler().to_curl(self.request)}"
            )
        raise ExecutorIsNotReady()
