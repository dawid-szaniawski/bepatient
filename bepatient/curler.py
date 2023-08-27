from shlex import quote
from typing import Any

from requests import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict


class Curler:
    """
    A class to convert a `PreparedRequest` or a `Response` object to a `curl` command.
    """

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _prepare_headers(data: dict[str, Any] | CaseInsensitiveDict[str]) -> str:
        headers = " ".join(
            (f"-H {quote(f'{name}: {value}')}" for name, value in data.items())
        )
        return f" {headers}" if len(headers) > 0 else ""

    @staticmethod
    def _prepare_body(data: str | bytes, charset: str) -> str:
        if isinstance(data, bytes):
            data = data.decode(charset)

        return f" -d {quote(data)}"

    def to_curl(
        self, request: PreparedRequest | Response, charset: str | None = None
    ) -> str:
        """A method to convert a `PreparedRequest` or a `Response` object to a `curl`
        command. Returns the `curl` command as a string.

        Args:
            request (PreparedRequest | Response): The `PreparedRequest` or `Response`
                object to be converted.
            charset (str, optional): The character set to use for encoding the
                request body, if it is a byte string. Defaults to "utf-8".

        Returns:
            the `curl` command as a string."""
        if not charset:
            charset = "utf-8"

        if isinstance(request, Response):
            request = request.request
            if "content-length" in request.headers:
                del request.headers["content-length"]

        curl_command = f"curl -X {quote(request.method)}"  # type: ignore
        curl_command += self._prepare_headers(request.headers)

        if request.body:
            curl_command += self._prepare_body(request.body, charset)

        curl_command += f" {request.url}"
        return curl_command
