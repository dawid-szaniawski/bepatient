from typing import Any

from requests import PreparedRequest, Request, Response, Session

from .curler import Curler
from .waiter_src import comparators
from .waiter_src.checkers import CHECKERS, RESPONSE_CHECKERS
from .waiter_src.checkers.checker import Checker
from .waiter_src.executors.requests_executor import RequestsExecutor
from .waiter_src.waiter import wait_for_executor


class RequestsWaiter:
    """Utility class for setting up and monitoring requests for expected values.

    Args:
        request (PreparedRequest | Request | Response): request or response to monitor.
        status_code (int, optional): The expected HTTP status code. Defaults to 200.
        session (Session | None, optional): The requests session to use for sending
            requests. Defaults to None.
        timeout (int | tuple[int, int] | None, optional): request timeout in seconds.
            Default value is 15 for connect and 30 for read (15, 30). If user provide
            one value, it will be applied to both - connect and read timeouts.

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
        request: PreparedRequest | Request | Response,
        status_code: int = 200,
        session: Session | None = None,
        timeout: int | tuple[int, int] | None = None,
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
        comparer: comparators.COMPARATORS,
        checker: CHECKERS = "json_checker",
        dict_path: str | None = None,
        search_query: str | None = None,
        ignore_case: bool = False,
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
            ignore_case (bool, optional): If set, upper/lower-case keys in dict_path
                are treated the same. Defaults to False.

        Returns:
            self: updated RequestsWaiter instance."""
        self.executor.add_checker(
            RESPONSE_CHECKERS[checker](  # type: ignore
                comparer=getattr(comparators, comparer),
                expected_value=expected_value,
                dict_path=dict_path,
                search_query=search_query,
                ignore_case=ignore_case,
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
    request: PreparedRequest | Request | Response,
    status_code: int = 200,
    comparer: comparators.COMPARATORS | None = None,
    expected_value: Any = None,
    checker: CHECKERS = "json_checker",
    session: Session | None = None,
    dict_path: str | None = None,
    search_query: str | None = None,
    retries: int = 60,
    delay: int = 1,
    req_timeout: int | tuple[int, int] | None = None,
) -> Response:
    """Wait for a specified value in a response.

    Args:
        request (PreparedRequest | Request | Response): The request or response to
            monitor for the expected value.
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
        req_timeout (int | tuple[int, int] | None, optional): request timeout in
            seconds. Default value is 15 for connect and 30 for read (15, 30). If user
            provide one value, it will be applied to both - connect and read timeouts.

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
    waiter = RequestsWaiter(
        request=request, status_code=status_code, session=session, timeout=req_timeout
    )

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
    request: PreparedRequest | Request | Response,
    checkers: list[dict[str, Any]],
    status_code: int = 200,
    session: Session | None = None,
    retries: int = 60,
    delay: int = 1,
    req_timeout: int | tuple[int, int] | None = None,
) -> Response:
    """Wait for multiple specified values in a response using different checkers.

    Args:
        request (PreparedRequest | Request | Response): The request or response to
            monitor for the expected values.
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
               - ignore_case (bool, optional): If set, upper/lower-case keys in
                    dict_path are treated the same. Defaults to False.
        status_code (int, optional): The expected HTTP status code. Defaults to 200.
        session (Session | None, optional): The requests session to use for sending
               requests. Defaults to None.
        retries (int, optional): The number of retries to perform. Defaults to 60.
        delay (int, optional): The delay between retries in seconds. Defaults to 1.
        req_timeout (int | tuple[int, int] | None, optional): request timeout in
            seconds. Default value is 15 for connect and 30 for read (15, 30). If user
            provide one value, it will be applied to both - connect and read timeouts.

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
    waiter = RequestsWaiter(
        request=request, status_code=status_code, session=session, timeout=req_timeout
    )

    for checker_dict in checkers:
        waiter.add_checker(**checker_dict)

    return waiter.run(retries=retries, delay=delay).get_result()


def dict_differences(
    expected_dict: dict[str, Any], actual_dict: dict[str, Any]
) -> dict[str, set[str] | dict[str, Any]]:
    """Compares two dictionaries and identifies the differences in keys and values.

    Args:
        expected_dict: dictionary with expected key-value pairs.
        actual_dict: dictionary with actual key-value pairs.

    Returns:
        dict: A dictionary containing the following information:
            - 'key_missing_exp' (set): Keys present in expected_dict but not in
                actual_dict.
            - 'key_missing_actual' (set): Keys present in actual_dict but not in
                expected_dict.
            - 'value_diff' (dict): Dictionary of differing key-value pairs, with keys
                present in both dictionaries and values not matching. Each differing
                pair is represented as
                {'expected': expected_value, 'actual': actual_value}.

    Example:
        ```python
            expected = {'a': 1, 'b': 2, 'c': 3}
            actual = {'a': 1, 'b': 5, 'd': 4}
            differences = dict_differences(expected, actual)
            print(differences)
        ```
    Output:
        ```
            {
                'key_missing_exp': {'c'},
                'key_missing_actual': {'d'},
                'value_diff': {'b': {'expected': 2, 'actual': 5}}
            }
        ```"""
    missing_k_exp = expected_dict.keys() - actual_dict.keys()
    missing_k_act = actual_dict.keys() - expected_dict.keys()

    value_diff = {
        key: {"expected": expected_dict[key], "actual": actual_dict[key]}
        for key in expected_dict.keys() & actual_dict.keys()
        if expected_dict[key] != actual_dict[key]
    }

    return {
        "key_missing_exp": missing_k_exp,
        "key_missing_actual": missing_k_act,
        "value_diff": value_diff,
    }


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
