import json
from typing import Any

import pytest
from pytest_mock import MockerFixture
from requests import PreparedRequest, Response, Session
from requests.models import CaseInsensitiveDict

from bepatient.waiter_src.checker import Checker


@pytest.fixture(scope="session")
def dict_content_response() -> Response:
    data = {
        "list_of_dicts": [{"name": "John", "age": 30}, {"name": "Mike", "age": 15}],
        "ok": True,
        "list": ["1", "2", "3"],
    }
    res = Response()
    res.status_code = 200
    res._content = json.dumps(data).encode("utf-8")  # pylint: disable=protected-access
    return res


@pytest.fixture(scope="session")
def headers_response() -> Response:
    res = Response()
    res.status_code = 200
    res.headers = CaseInsensitiveDict(name="John", age="30", list="['1', '2', '3']")
    return res


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


@pytest.fixture
def session_mock(
    mocker: MockerFixture,
    dict_content_response: Response,  # pylint: disable=redefined-outer-name
) -> Session:
    session = mocker.MagicMock()
    session.send.return_value = dict_content_response
    return session


@pytest.fixture(scope="session")
def checker() -> Checker:
    class CheckerMocker(Checker):
        def __str__(self) -> str:
            return "The truth"

        def check(self, data: Any) -> bool:
            return True

    return CheckerMocker()


@pytest.fixture(scope="session")
def checker_false() -> Checker:
    class CheckerMocker(Checker):
        def __str__(self):
            return "I'm falsy"

        def check(self, data: Any) -> bool:
            return False

    return CheckerMocker()
