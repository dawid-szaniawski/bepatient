import logging
from abc import abstractmethod
from json import JSONDecodeError
from typing import Any, Callable
from uuid import uuid4

from dictor import dictor
from requests import Response

from bepatient.waiter_src.checker import Checker

log = logging.getLogger(__name__)


class ResponseChecker(Checker):
    """A checker that compares a value in a response against an expected value.

    Args:
        comparer (Callable): A function that performs the comparison.
        expected_value (Any): The expected value to compare against."""

    def __init__(self, comparer: Callable[[Any, Any], bool], expected_value: Any):
        self.comparer = comparer
        self.expected_value = expected_value
        self._prepared_data: dict[str, Any] | list[Any] | int | None = None

    def __str__(self) -> str:
        attrs = self.__dict__.copy()
        del attrs["_prepared_data"]
        attrs["checker"] = self.__class__.__name__
        attrs["comparer"] = self.comparer.__name__

        return (
            " | ".join([f"{k.capitalize()}: {v}" for k, v in sorted(attrs.items())])
            + f" | Data: {self._prepared_data}"
        )

    @abstractmethod
    def prepare_data(self, data: Response, run_uuid: str | None = None) -> Any:
        """Prepare the data from the response for comparison.

        Args:
            data (Response): response containing the data.
            run_uuid (str | None): unique run identifier. Defaults to None.

        Returns:
            Any: Data for comparison."""
        ...

    def check(self, data: Response) -> bool:
        """Checks if the value in the JSON response satisfies the condition.

        Args:
            data (Response): response containing the JSON data.

        Returns:
            bool: True if the value in the JSON response satisfies the condition,
                False otherwise."""
        run_uuid = str(uuid4())
        log.info("Check uuid: %s | %s", run_uuid, self)

        try:
            self._prepared_data = self.prepare_data(data, run_uuid)
            if self.comparer(self._prepared_data, self.expected_value):
                return True
            log.debug(
                "Check uuid: %s | Condition not met | Expected: %s | Data: %s",
                run_uuid,
                self.expected_value,
                self._prepared_data,
            )
        except (TypeError, JSONDecodeError):
            log.exception(
                "Check uuid: %s | Expected: %s | Headers: %s | Content %s",
                run_uuid,
                self.expected_value,
                data.headers,
                data.content,
            )

        return False


class StatusCodeChecker(ResponseChecker):
    def prepare_data(self, data: Response, run_uuid: str | None = None) -> int:
        """Prepare the response status code for comparison.

        Args:
            data (Response): response containing the status code.
            run_uuid (str | None, optional): unique run identifier. Defaults to None.

        Returns:
            int: prepared status code for comparison."""
        status_code = data.status_code
        log.info("Check uuid: %s | Response status code: %s", run_uuid, status_code)
        return status_code


class DictResponseChecker(ResponseChecker):
    """A checker that compares a value in a response against an expected value.

    Args:
        comparer (Callable): A function that performs the comparison.
        expected_value (Any): The expected value to compare against.
        dict_path (str, optional): dot-separated path to the value in the response data.
            Defaults to None.
        search_query (str, optional): A search query to find the value in the response
            data. Defaults to None.
        dictor_fallback (str, optional): A default value to return if the value at the
            specified path is not found using `dictor`. Defaults to None."""

    def __init__(
        self,
        comparer: Callable[[Any, Any], bool],
        expected_value: Any,
        dict_path: str | None = None,
        search_query: str | None = None,
        dictor_fallback: str | None = None,
    ):
        self.path = dict_path
        self.search_query = search_query
        self.dictor_fallback = dictor_fallback
        super().__init__(comparer, expected_value)

    @staticmethod
    @abstractmethod
    def parse_response(
        data: Response, run_uuid: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Parse the response data into a dictionary or a list for comparison.

        Args:
            data (Response): response containing the data.
            run_uuid (str | None): The unique run identifier. Defaults to None.

        Returns:
            dict[str, Any] | list[Any]: The parsed response data for comparison."""
        ...

    def prepare_data(
        self, data: Response, run_uuid: str | None = None
    ) -> dict[str, Any] | list[Any] | None:
        """Prepare the response data for comparison.

        Args:
            data (Response): The response containing the data.
            run_uuid (str | None): The unique run identifier. Defaults to None.

        Returns:
            dict[str, Any] | list[Any] | None: The prepared data for comparison."""
        try:
            return dictor(
                self.parse_response(data, run_uuid),
                self.path,
                search=self.search_query,
                default=self.dictor_fallback,
            )
        except (TypeError, JSONDecodeError):
            log.exception(
                "Check uuid: %s | Expected: %s | Headers: %s | Content %s",
                run_uuid,
                self.expected_value,
                data.headers,
                data.content,
            )
        return None


class JsonChecker(DictResponseChecker):
    """A checker that compares a value in a JSON response against an expected value.

    Example:
        To check if a specific field "status" in a JSON response equals 200:

        ```
            checker = JsonChecker(lambda a, b: a == b, 200, dict_path="status")
            assert checker.check(response) is True
        ```"""

    @staticmethod
    def parse_response(
        data: Response, run_uuid: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Parse the response content as JSON for comparison.

        Args:
            data (Response): The response containing the JSON data.
            run_uuid (str | None): The unique run identifier. Defaults to None.

        Returns:
            dict[str, Any] | list[Any]: The parsed JSON response data for comparison."""
        log.info("Check uuid: %s | Response content: %s", run_uuid, data.content)
        return data.json()


class HeadersChecker(DictResponseChecker):
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
        log.info("Check uuid: %s | Response headers: %s", run_uuid, headers)
        return headers
