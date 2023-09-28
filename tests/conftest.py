import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pytest
from pytest_mock import MockerFixture
from requests import PreparedRequest, Response, Session
from requests.models import CaseInsensitiveDict

SCRIPTS_PATH = Path(__file__) / "../scripts/"


@pytest.fixture(scope="session")
def dict_content_response() -> Response:
    data = {
        "list_of_dicts": [{"name": "John", "age": 30}, {"name": "Mike", "age": 15}],
        "ok": True,
        "list": ["1", "2", "3"],
        "none": None,
        "empty": "",
        "false": False,
        "name": "Jack",
    }
    res = Response()
    res.status_code = 200
    res.headers = CaseInsensitiveDict(content="json")
    res._content = json.dumps(data).encode("utf-8")
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


@pytest.fixture
def is_equal() -> Callable[[Any, Any], bool]:
    def comparer(data: Any, expected_value: Any) -> bool:
        return data == expected_value

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


@pytest.fixture
def sqlite_db(tmp_path: Path) -> sqlite3.Cursor:  # type: ignore
    def dict_factory(
        cur: sqlite3.Cursor, row: tuple[str | int | datetime]
    ) -> dict[str, str | int | datetime]:
        fields = [column[0] for column in cur.description]
        return dict(zip(fields, row))

    conn = sqlite3.connect(
        database=os.path.join(tmp_path, "bepatient.sqlite"),
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    conn.row_factory = dict_factory
    with open(SCRIPTS_PATH / "init_db.sql", mode="r", encoding="utf-8") as file:
        conn.executescript(file.read())
    cursor = conn.cursor()
    yield cursor
    cursor.close()
    conn.close()


@pytest.fixture
def select_all_from_user_query() -> str:
    return "SELECT * from user"
