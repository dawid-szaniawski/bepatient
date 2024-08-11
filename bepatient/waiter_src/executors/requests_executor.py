import logging
import uuid

from requests import PreparedRequest, Request, Response, Session
from requests.exceptions import RequestException

from bepatient.curler import Curler
from bepatient.waiter_src.checkers.response_checkers import StatusCodeChecker
from bepatient.waiter_src.comparators import is_equal

from .executor import Executor

log = logging.getLogger(__name__)


# pylint: disable-next=too-many-instance-attributes
class RequestsExecutor(Executor):
    """An executor that sends a request and waits for a certain condition to be met.
    Args:
        req_or_res (PreparedRequest | Request | Response): request to send.
        expected_status_code (int): expected HTTP status code of the response
        session (Session | None, optional): requests session to use.
        timeout (int | tuple[int, int] | None, optional): request timeout in seconds.
            Default value is 15 for connect and 30 for read (15, 30). If user provide
            one value, it will be applied to both - connect and read timeouts."""

    def __init__(
        self,
        req_or_res: PreparedRequest | Request | Response,
        expected_status_code: int,
        session: Session | None = None,
        timeout: int | tuple[int, int] | None = None,
    ):
        super().__init__()
        self._result: Response | None = None
        self._take_from_result: bool = False
        self._status_code_checker = StatusCodeChecker(is_equal, expected_status_code)

        if timeout:
            self.timeout = timeout
        else:
            self.timeout = (15, 30)

        if session:
            self.session = session
        else:
            log.debug("Creating a new Session object")
            self.session = Session()

        if isinstance(req_or_res, Request):
            self.request = self.session.prepare_request(req_or_res)
        elif isinstance(req_or_res, PreparedRequest):
            self.request = req_or_res
        else:
            self._result = req_or_res
            self._take_from_result = True
            if len(self._result.history) > 0:
                self.request = self._result.history[0].request
            else:
                self.request = self._result.request
            self._merge_session_data_to_prepared_request()

        self._input = Curler().to_curl(self.request)

    def _merge_session_data_to_prepared_request(self):
        log.debug("Merging session.headers into PreparedRequest object")
        self.request.headers.update(self.session.headers)  # type: ignore
        if self.session.cookies:
            log.debug("Merging session.cookies into PreparedRequest object")
            req_cookies = self.request.headers.get("Cookie", "")
            if req_cookies:
                log.debug("PreparedRequest already has cookies")
                req_cookies = req_cookies + "; "
            session_cookies = "; ".join(
                f"{k}={v}" for k, v in self.session.cookies.items()
            )
            self.request.headers["Cookie"] = req_cookies + session_cookies

    def is_condition_met(self) -> bool:
        """Sends the request and check if all checkers pass or timeout occurs.

        Returns:
            bool: True if all checkers pass, False otherwise.

        Raises:
            ExecutorIsNotReady: If the executor is not ready to send the request."""
        run_uuid: str = str(uuid.uuid4())
        if not self._take_from_result:
            try:
                self._result = self.session.send(
                    request=self.request, timeout=self.timeout
                )
                self._input = Curler().to_curl(self._result)
                log.debug("Sent: %s", self._input)
            except RequestException:
                log.exception("RequestException! CURL: %s", self._input)
                return False
        else:
            self._take_from_result = False

        if self._status_code_checker.check(self._result, run_uuid):
            self._failed_checkers = [
                checker
                for checker in self._checkers
                if not checker.check(self._result, run_uuid)
            ]
        else:
            self._failed_checkers = [self._status_code_checker]

        if len(self._failed_checkers) == 0:
            return True
        return False
