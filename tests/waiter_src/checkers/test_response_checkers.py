from json import JSONDecodeError
from typing import Any, Callable

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from requests import Response

from bepatient.waiter_src.checkers.response_checkers import (
    HeadersChecker,
    JsonChecker,
    StatusCodeChecker,
)


class TestStatusCodeChecker:
    def test_str(self, is_equal: Callable[[Any, Any], bool]):
        checker = StatusCodeChecker(is_equal, 5)
        msg = (
            "Checker: StatusCodeChecker | Comparer: comparer | "
            "Expected_value: 5 | Data: None"
        )

        assert str(checker) == msg

    def test_prepare_data(
        self,
        headers_response: Response,
        is_equal: Callable[[Any, Any], bool],
        caplog: LogCaptureFixture,
    ):
        checker = StatusCodeChecker(is_equal, 200)
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: None | Response status code: 200",
            )
        ]

        assert checker.prepare_data(headers_response) == 200
        assert caplog.record_tuples == logs

    def test_check(
        self,
        headers_response: Response,
        is_equal: Callable[[Any, Any], bool],
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        checker = StatusCodeChecker(is_equal, 200)
        monkeypatch.setattr("uuid.uuid4", lambda: "TestStatusCodeChecker")
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestStatusCodeChecker | Checker: StatusCodeChecker | "
                "Comparer: comparer | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestStatusCodeChecker | Response status code: 200",
            ),
        ]

        assert checker.check(headers_response) is True
        assert caplog.record_tuples == logs


class TestJsonChecker:
    def test_str(self, is_equal: Callable[[Any, Any], bool]):
        checker = JsonChecker(is_equal, 5)
        msg = (
            "Checker: JsonChecker | Comparer: comparer | Dictor_fallback: None |"
            " Expected_value: 5 | Path: None | Search_query: None | Data: None"
        )

        assert str(checker) == msg

    def test_dict(
        self, dict_content_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = JsonChecker(is_equal, True, dict_path="ok")
        assert checker.check(dict_content_response) is True

    def test_list(self, dict_content_response: Response):
        checker = JsonChecker(lambda a, b: b in a, "2", dict_path="list")
        assert checker.check(dict_content_response) is True

    def test_longer_dict_path(self, dict_content_response: Response):
        checker = JsonChecker(lambda a, b: a < b, 18, dict_path="list_of_dicts.1.age")
        assert checker.check(dict_content_response) is True

    def test_search_query(
        self, dict_content_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = JsonChecker(
            comparer=is_equal,
            expected_value=["John", "Mike"],
            dict_path="list_of_dicts",
            search_query="name",
        )
        assert checker.check(dict_content_response) is True

    def test_condition_not_met(self, dict_content_response: Response):
        checker = JsonChecker(
            lambda a, b: b in a, "Joe", dict_path="list_of_dicts", search_query="name"
        )
        assert checker.check(dict_content_response) is False

    def test_missing_key(
        self, dict_content_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = JsonChecker(is_equal, "TEST", dict_path="status")
        assert checker.check(dict_content_response) is False

    def test_missing_in_search_query(
        self, dict_content_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = JsonChecker(is_equal, "TEST", search_query="name")
        assert checker.check(dict_content_response) is False

    @pytest.mark.xfail(reason="The dictor library bug")
    def test_null_value(
        self,
        dict_content_response: Response,
        is_equal: Callable[[Any, Any], bool],
    ):
        checker = JsonChecker(is_equal, None, dict_path="none", dictor_fallback="Empty")
        assert checker.prepare_data(dict_content_response) is None

    def test_prepare_data_catch_json_decode_error(
        self,
        mocker: MockerFixture,
        caplog: LogCaptureFixture,
        is_equal: Callable[[Any, Any], bool],
    ):
        def json_mock():
            raise JSONDecodeError("", "", 1)

        response = mocker.MagicMock()
        response.url = "https://webludus.pl"
        response.status_code = 200
        response.content = bytes('{ "name', "utf-8")
        response.headers = {"error": "JSONDecodeError"}
        response.json = json_mock
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: None | Response content: b'{ \"name'",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                40,
                "Check uuid: None | Expected: TEST"
                " | Headers: {'error': 'JSONDecodeError'} | Content b'{ \"name'",
            ),
        ]

        data = JsonChecker(is_equal, "TEST", search_query="name").prepare_data(response)
        assert data is None
        assert caplog.record_tuples == logs

    def test_prepare_data_catch_type_error(
        self,
        mocker: MockerFixture,
        caplog: LogCaptureFixture,
        is_equal: Callable[[Any, Any], bool],
    ):
        def json_mock():
            raise TypeError("", "", 1)

        response = mocker.MagicMock()
        response.url = "https://webludus.pl"
        response.status_code = 200
        response.content = bytes('{ "name', "utf-8")
        response.headers = {"error": "TypeError"}
        response.json = json_mock
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: None | Response content: b'{ \"name'",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                40,
                "Check uuid: None | Expected: TEST | Headers: {'error': 'TypeError'} | "
                "Content b'{ \"name'",
            ),
        ]

        data = JsonChecker(is_equal, "TEST", search_query="name").prepare_data(response)
        assert data is None
        assert caplog.record_tuples == logs


class TestHeadersChecker:
    def test_str(self, is_equal: Callable[[Any, Any], bool]):
        checker = HeadersChecker(is_equal, 5)
        msg = (
            "Checker: HeadersChecker | Comparer: comparer | Dictor_fallback: None |"
            " Expected_value: 5 | Path: None | Search_query: None | Data: None"
        )

        assert str(checker) == msg

    def test_dict(
        self,
        headers_response: Response,
        is_equal: Callable[[Any, Any], bool],
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("uuid.uuid4", lambda: "TestHeadersChecker")
        checker = HeadersChecker(is_equal, "John", dict_path="name")
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Checker: HeadersChecker"
                " | Comparer: comparer | Dictor_fallback: None | Expected_value: John"
                " | Path: name | Search_query: None | Data: John",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Response headers: "
                "{'name': 'John', 'age': '30', 'list': \"['1', '2', '3']\"}",
            ),
        ]
        assert checker.check(headers_response) is True
        assert caplog.record_tuples == logs

    def test_search_query(
        self, headers_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = HeadersChecker(
            comparer=is_equal, expected_value=["['1', '2', '3']"], search_query="list"
        )
        assert checker.check(headers_response) is True

    def test_condition_not_met(
        self,
        headers_response: Response,
        is_equal: Callable[[Any, Any], bool],
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("uuid.uuid4", lambda: "TestHeadersChecker")
        checker = HeadersChecker(is_equal, "Joe", dict_path="name")
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Checker: HeadersChecker | Comparer: "
                "comparer | Dictor_fallback: None | Expected_value: Joe | Path: name | "
                "Search_query: None | Data: John",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker |"
                " Response headers: {'name': 'John', 'age': '30', "
                "'list': \"['1', '2', '3']\"}",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TestHeadersChecker | Condition not met"
                " | Expected: Joe | Data: John",
            ),
        ]
        assert checker.check(headers_response) is False
        assert caplog.record_tuples == logs

    def test_missing_key(
        self, headers_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = HeadersChecker(is_equal, "TEST", dict_path="status")
        assert checker.check(headers_response) is False

    def test_missing_in_search_query(
        self, headers_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = HeadersChecker(is_equal, "TEST", search_query="name")
        assert checker.check(headers_response) is False
