from typing import Any

from requests import PreparedRequest, Response, Session

from .curler import Curler
from .waiter_src.checker import Checker
from .waiter_src.checkers import CHECKERS, RESPONSE_CHECKERS
from .waiter_src.comparators import COMP_DICT, COMPARATORS
from .waiter_src.executors.requests_executor import RequestsExecutor
from .waiter_src.waiter import wait_for_executor


def to_curl(req_or_res: PreparedRequest | Response, charset: str | None = None) -> str:
    """Converts a `PreparedRequest` or a `Response` object to a `curl` command.

    Args:
        req_or_res (PreparedRequest | Response): The `PreparedRequest` or `Response`
            object to be converted.
        charset (str, optional): The character set to use for encoding the
            request body, if it is a byte string. Defaults to "utf-8".

    Returns:
        the `curl` command as a string"""
    return Curler().to_curl(req_or_res, charset)


class RequestsWaiter:
    """Utility class for setting up and monitoring requests for expected values.

    Args:
        request (PreparedRequest | Response): request or response to monitor.
        status_code (int, optional): The expected HTTP status code. Defaults to 200.
        session (Session | None, optional): The requests session to use for sending
            requests. Defaults to None.
        timeout (int | None, optional): request timeout in seconds.

    Example:
        To wait for a JSON response where the "status" field equals 200 using a
            RequestsWaiter:
        ```
            waiter = RequestsWaiter(request=requests, status_code=200, session=session)
            response = waiter.add_checker(
                expected_value=0,
                comparer="have_len_greater",
                checker="json_checker",
                dict_path="data"
            ).run(retries=5, delay=2).get_result()
        ```"""

    def __init__(
        self,
        request: PreparedRequest | Response,
        status_code: int = 200,
        session: Session | None = None,
        timeout: int = 5,
    ):
        self.executor = RequestsExecutor(
            req_or_res=request,
            expected_status_code=status_code,
            session=session,
            timeout=timeout,
        )

    def add_checker(
        self,
        expected_value: Any,
        comparer: COMPARATORS,
        checker: CHECKERS = "json_checker",
        dict_path: str | None = None,
        search_query: str | None = None,
    ):
        """Add a response checker to the waiter.

        Args:
            expected_value (Any): The value to be compared against the response data.
            comparer (COMPARATORS): The comparer function or operator used for
                value comparison.
            checker (CHECKERS, optional): The type of checker to use. Defaults to
                "json_checker".
            dict_path (str | None, optional): The dot-separated path to the value in the
                response data. Defaults to None.
            search_query (str | None, optional): A search query to use to find the value
                in the response data. Defaults to None.

        Returns:
            self: updated RequestsWaiter instance."""
        self.executor.add_checker(
            RESPONSE_CHECKERS[checker](  # type: ignore
                comparer=COMP_DICT[comparer],
                expected_value=expected_value,
                dict_path=dict_path,
                search_query=search_query,
            )
        )
        return self

    def add_custom_checker(self, checker: Checker):
        """Add a custom response checker to the waiter.
        This method allows users to add their own custom response checker by providing
        an object that inherits from the abstract base class Checker.

        Args:
            checker (Checker): An instance of a custom checker object that inherits
                from the Checker class.

        Returns:
            self: updated RequestsWaiter instance."""
        self.executor.add_checker(checker)
        return self

    def run(self, retries: int = 60, delay: int = 1, raise_error: bool = True):
        """Run the waiter and monitor the specified request or response.

        Args:
            retries (int, optional): The number of retries to perform. Defaults to 60.
            delay (int, optional): The delay between retries in seconds. Defaults to 1.
            raise_error (bool): raises WaiterConditionWasNotMet.

        Returns:
            self: updated RequestsWaiter instance.

        Raises:
            WaiterConditionWasNotMet: if the condition is not met within the specified
                number of attempts."""
        wait_for_executor(
            executor=self.executor,
            retries=retries,
            delay=delay,
            raise_error=raise_error,
        )
        return self

    def get_result(self) -> Response:
        """Get the final response containing the expected values.

        Returns:
            Response: final response containing the expected values."""
        return self.executor.get_result()


def wait_for_value_in_request(
    request: PreparedRequest | Response,
    status_code: int = 200,
    comparer: COMPARATORS | None = None,
    expected_value: Any = None,
    checker: CHECKERS = "json_checker",
    session: Session | None = None,
    dict_path: str | None = None,
    search_query: str | None = None,
    retries: int = 60,
    delay: int = 1,
) -> Response:
    """Wait for a specified value in a response.

    Args:
        request (PreparedRequest | Response): The request or response to monitor for
            the expected value.
        status_code (int, optional): The expected HTTP status code. Defaults to 200.
        comparer (COMPARATORS | None, optional): The comparer function or operator used
            for value comparison. Defaults to None.
        expected_value (Any, optional): The value to be compared against the response
            data. Defaults to None.
        checker (CHECKERS, optional): The type of checker to use.
        session (Session | None, optional): The requests session to use for sending
            requests. Defaults to None.
        dict_path (str | None, optional): The dot-separated path to the value in the
            response data. Defaults to None.
        search_query (str | None, optional): A search query to use to find the value in
            the response data. Defaults to None.
        retries (int, optional): The number of retries to perform. Defaults to 60.
        delay (int, optional): The delay between retries in seconds. Defaults to 1.

    Returns:
        Response: the final response containing the expected value.

    Raises:
        WaiterConditionWasNotMet: if the condition is not met within the specified
            number of attempts.

    Example:
        To wait for a JSON response where the "status" field equals 200 and request
            returns list of dict.
        ```
            response = wait_for_value_in_requests(
                requests=request,
                status_code=200,
                comparer="have_len_greater",
                expected_value=0,
                checker="json_checker",
                session=session,
                dict_path="data",
            )
        ```"""
    waiter = RequestsWaiter(request=request, status_code=status_code, session=session)

    if comparer:
        waiter.add_checker(
            comparer=comparer,
            checker=checker,
            expected_value=expected_value,
            dict_path=dict_path,
            search_query=search_query,
        )

    return waiter.run(retries=retries, delay=delay).get_result()


def wait_for_values_in_request(
    request: PreparedRequest | Response,
    checkers: list[dict[str, Any]],
    status_code: int = 200,
    session: Session | None = None,
    retries: int = 60,
    delay: int = 1,
) -> Response:
    """Wait for multiple specified values in a response using different checkers.

    Args:
        request (PreparedRequest | Response): The request or response to monitor for the
            expected values.
        checkers (list[dict[str, Any]]): A list of dictionaries, where each dictionary
            contains information about a checker to apply.
            Each dictionary must have keys:
               - checker (CHECKERS): type of checker to use.
               - comparer (COMPARATORS): comparer function or operator used for value
                    comparison.
               - expected_value (Any): the value to be compared against the response
                    data.
               - dict_path (str | None, optional): The dot-separated path to the value
                    in the response data. Defaults to None.
               - search_query (str | None, optional): A search query to use to find the
                    value in the response data. Defaults to None.
        status_code (int, optional): The expected HTTP status code. Defaults to 200.
        session (Session | None, optional): The requests session to use for sending
               requests. Defaults to None.
        retries (int, optional): The number of retries to perform. Defaults to 60.
        delay (int, optional): The delay between retries in seconds. Defaults to 1.

    Returns:
        Response: the final response containing the expected values.

    Raises:
        WaiterConditionWasNotMet: if the condition is not met within the specified
            number of attempts.

    Example:
        To wait for multiple conditions using different checkers:
        ```
           checkers = [
               {
                   "checker": "json_checker",
                   "comparer": "have_len_greater",
                   "expected_value": 0,
                   "dict_path": "data",
               },
               {
                   "checker": "json_checker",
                   "comparer": "is_equal",
                   "expected_value": "success",
                   "search_query": "message",
               }
           ]

           response = wait_for_values_in_request(
               request=request,
               checkers=checkers,
               status_code=200,
               session=session,
               retries=5
           )
        ```"""
    waiter = RequestsWaiter(request=request, status_code=status_code, session=session)

    for checker_dict in checkers:
        waiter.add_checker(**checker_dict)

    return waiter.run(retries=retries, delay=delay).get_result()
