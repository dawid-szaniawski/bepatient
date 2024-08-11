import logging
from json import JSONDecodeError
from typing import Any, Callable

from dictor import dictor
from requests import Response

from .checker import Checker

log = logging.getLogger(__name__)


class StatusCodeChecker(Checker):
    def prepare_data(self, data: Response, run_uuid: str | None = None) -> int:
        """Prepare the response status code for comparison.

        Args:
            data (Response): response containing the status code.
            run_uuid (str | None, optional): unique run identifier. Defaults to None.

        Returns:
            int: prepared status code for comparison."""
        status_code = data.status_code
        log.debug(
            "Check uuid: %s | Response status code: %s | Response content: %s",
            run_uuid,
            status_code,
            data.content,
        )
        return status_code


class JsonChecker(Checker):
    """A checker that compares a value in a JSON response against an expected value.

    Args:
        comparer (Callable): A function that performs the comparison.
        expected_value (Any): The expected value to compare against.
        dict_path (str, optional): dot-separated path to the value in the response data.
            Defaults to None.
        search_query (str, optional): A search query to find the value in the response
            data. Defaults to None.
        dictor_fallback (str, optional): A default value to return if the value at the
            specified path is not found using `dictor`. Defaults to None.
        ignore_case (bool, optional): If set, upper/lower-case keys in dict_path are
            treated the same. Defaults to False.

    Example:
        To check if a specific field "status" in a JSON response equals 200:

        ```
            checker = JsonChecker(lambda a, b: a == b, 200, dict_path="status")
            assert checker.check(response) is True
        ```"""

    def __init__(
        self,
        comparer: Callable[[Any, Any], bool],
        expected_value: Any,
        dict_path: str | None = None,
        search_query: str | None = None,
        dictor_fallback: str | None = None,
        ignore_case: bool = False,
    ):
        super().__init__(comparer, expected_value)
        self.path = dict_path
        self.search_query = search_query
        self.dictor_fallback = dictor_fallback
        self.ignore_case = ignore_case

    @staticmethod
    def parse_response(
        data: Response, run_uuid: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Parse the response content as JSON for comparison.

        Args:
            data (Response): response containing the JSON data.
            run_uuid (str | None): unique run identifier. Defaults to None.

        Returns:
            dict[str, Any] | list[Any]: The parsed JSON response data for comparison."""
        log.debug("Check uuid: %s | Response content: %s", run_uuid, data.content)
        return data.json()

    def prepare_data(self, data: Response, run_uuid: str | None = None) -> Any:
        """Prepare the response data for comparison.

        Args:
            data (Response): The response containing the data.
            run_uuid (str | None): The unique run identifier. Defaults to None.

        Returns:
            Any: The prepared data for comparison."""
        try:
            dictor_data = dictor(
                data=self.parse_response(data, run_uuid),
                path=self.path,
                search=self.search_query,
                default=self.dictor_fallback,
                ignorecase=self.ignore_case,
            )
            log.debug(
                "Check uuid: %s | Dictor path: %s"
                " | Dictor search: %s | Dictor data: %s",
                run_uuid,
                self.path,
                self.search_query,
                dictor_data,
            )
            return dictor_data
        except (TypeError, JSONDecodeError):
            log.exception(
                "Check uuid: %s | Expected: %s | Headers: %s | Content %s",
                run_uuid,
                self.expected_value,
                data.headers,
                data.content,
            )
        return None


class HeadersChecker(JsonChecker):
    """A checker that compares response headers against expected values.

    Example:
        To check if the "Content-Type" header in a response is "application/json":
        ```
            checker = HeadersChecker(
                lambda a, b: a == b, "application/json", dict_path="Content-Type"
            )
            assert checker.check(response) is True
        ```
    """

    @staticmethod
    def parse_response(data: Response, run_uuid: str | None = None) -> dict[str, str]:
        """Parse the response headers for comparison.

        Args:
            data (Response): The response containing the headers.
            run_uuid (str | None): The unique run identifier. Defaults to None.

        Returns:
            dict[str, str]: The parsed response headers for comparison."""
        headers = dict(data.headers)
        log.debug("Check uuid: %s | Response headers: %s", run_uuid, headers)
        return headers
