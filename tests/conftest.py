# pylint: disable=redefined-outer-name
import json
from typing import Any, Callable

import pytest
from pytest_mock import MockerFixture
from requests import PreparedRequest, Request, Response, Session
from requests.models import CaseInsensitiveDict
from responses import RequestsMock


@pytest.fixture
def mocked_responses() -> RequestsMock:  # type: ignore
    """Yields responses.RequestsMock as a context manager."""
    with RequestsMock() as response:
        yield response


# noinspection PyUnresolvedReferences
@pytest.fixture
def example_response_headers() -> CaseInsensitiveDict[str]:
    headers: CaseInsensitiveDict[str] = CaseInsensitiveDict()
    headers["Content-Language"] = "en-US"
    headers["Content-Type"] = "application/json"
    headers["server"] = "WebLudus.pl"
    headers["X-Render-Origin_Server"] = "gunicorn"
    return headers


@pytest.fixture
def example_request_headers() -> dict[str, str | bytes]:
    return {
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;",
        "Host": "webludus.pl",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101",
    }


@pytest.fixture
def example_dict_content() -> dict[str, Any]:
    return {
        "list_of_dicts": [{"name": "John", "age": 30}, {"name": "Mike", "age": 15}],
        "ok": True,
        "some_number": 123,
        "list": ["1", "2", "3"],
        "none": None,
        "empty": "",
        "false": False,
        "name": "Jack",
    }


@pytest.fixture
def request_object() -> Request:
    return Request(
        method="get",
        url="https://webludus.pl",
        headers={"task": "test"},
        cookies={"user-token": "abc-123"},
    )


@pytest.fixture
def prepared_request() -> PreparedRequest:
    request = PreparedRequest()
    request.prepare(
        method="get",
        url="https://webludus.pl",
        headers={"task": "test"},
        cookies={"user-token": "abc-123"},
    )
    return request


# noinspection PyUnresolvedReferences
@pytest.fixture
def example_response(
    example_response_headers: CaseInsensitiveDict[str],
    example_dict_content: dict[str, Any],
    prepared_request: PreparedRequest,
) -> Response:
    res = Response()
    res.status_code = 200
    res.headers = example_response_headers
    res._content = json.dumps(example_dict_content).encode("utf-8")
    res.request = prepared_request
    return res


# noinspection PyUnresolvedReferences
@pytest.fixture
def session_mock(
    mocker: MockerFixture,
    example_request_headers: dict[str, str],
    example_response: Response,
) -> Session:
    session = mocker.MagicMock()
    session.headers = example_request_headers
    session.send.return_value = example_response
    return session


# noinspection PyUnresolvedReferences
@pytest.fixture
def session_object(example_request_headers: dict[str, str | bytes]) -> Session:
    session = Session()
    session.headers = example_request_headers
    session.cookies["pytest"] = "fixture"
    return session


@pytest.fixture
def is_equal_comparer() -> Callable[[Any, Any], bool]:
    def comparer(data: Any, expected_value: Any) -> bool:
        return data == expected_value

    return comparer


@pytest.fixture
def contain_comparer() -> Callable[[Any, Any], bool]:
    def comparer(data: Any, expected_value: Any) -> bool:
        return expected_value in data

    return comparer


@pytest.fixture(scope="session")
def error_msg() -> str:
    return (
        "The condition has not been met! | Failed checkers: (Checker:"
        " JsonChecker | Comparer: is_equal | Dictor_fallback: None"
        " | Expected_value: False | Path: ok | Search_query: None | Data: True)"
        " | curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123'"
        " https://webludus.pl/"
    )
