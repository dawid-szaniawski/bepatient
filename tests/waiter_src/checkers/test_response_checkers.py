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
    def test_str(self, is_equal_comparer: Callable[[Any, Any], bool]):
        checker = StatusCodeChecker(is_equal_comparer, 5)
        msg = (
            "Checker: StatusCodeChecker | Comparer: comparer | "
            "Expected_value: 5 | Data: None"
        )

        assert str(checker) == msg

    def test_prepare_data(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
        caplog: LogCaptureFixture,
    ):
        checker = StatusCodeChecker(is_equal_comparer, 200)
        logs = [
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: None | Response status code: 200 | Response content:"
                ' b\'{"list_of_dicts": [{"name": "John", "age": 30},'
                ' {"name": "Mike", "age": 15}], "ok": true, "some_number": 123,'
                ' "list": ["1", "2", "3"], "none": null, "empty": "", "false": false,'
                ' "name": "Jack"}\'',
            )
        ]

        assert checker.prepare_data(example_response) == 200
        assert caplog.record_tuples == logs

    def test_check(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        checker = StatusCodeChecker(is_equal_comparer, 200)
        monkeypatch.setattr("uuid.uuid4", lambda: "TestStatusCodeChecker")
        logs = [
            (
                "bepatient.waiter_src.checker",
                20,
                "Check uuid: TestStatusCodeChecker | Checker: StatusCodeChecker"
                " | Comparer: comparer | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestStatusCodeChecker | Response status code: 200"
                ' | Response content: b\'{"list_of_dicts": [{"name": "John", "age": 30}'
                ', {"name": "Mike", "age": 15}], "ok": true, "some_number": 123, "list"'
                ': ["1", "2", "3"], "none": null, "empty": "", "false": false'
                ', "name": "Jack"}\'',
            ),
            (
                "bepatient.waiter_src.checker",
                10,
                "Check success! | uuid: TestStatusCodeChecker"
                " | Checker: StatusCodeChecker | Comparer: comparer"
                " | Expected_value: 200 | Data: 200",
            ),
        ]

        assert checker.check(example_response) is True
        assert caplog.record_tuples == logs


class TestJsonChecker:
    def test_str(self, is_equal_comparer: Callable[[Any, Any], bool]):
        checker = JsonChecker(is_equal_comparer, 5)
        msg = (
            "Checker: JsonChecker | Comparer: comparer | Dictor_fallback: None |"
            " Expected_value: 5 | Path: None | Search_query: None | Data: None"
        )

        assert str(checker) == msg

    def test_dict(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer, expected_value=True, dict_path="ok"
        )
        assert checker.check(example_response) is True

    def test_list(
        self, contain_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = JsonChecker(
            comparer=contain_comparer, expected_value="2", dict_path="list"
        )
        assert checker.check(example_response) is True

    def test_longer_dict_path(self, example_response: Response):
        checker = JsonChecker(
            comparer=lambda a, b: a < b,
            expected_value=18,
            dict_path="list_of_dicts.1.age",
        )
        assert checker.check(example_response) is True

    def test_search_query(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=["John", "Mike"],
            dict_path="list_of_dicts",
            search_query="name",
        )
        assert checker.check(example_response) is True

    def test_condition_not_met(
        self, contain_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = JsonChecker(
            comparer=contain_comparer,
            expected_value="Joe",
            dict_path="list_of_dicts",
            search_query="name",
        )
        assert checker.check(example_response) is False

    def test_missing_key(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer, expected_value="TEST", dict_path="status"
        )
        assert checker.check(example_response) is False

    def test_missing_in_search_query(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer, expected_value="TEST", search_query="name"
        )
        assert checker.check(example_response) is False

    def test_null_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            dict_path="none",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) is None

    def test_empty_string_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            dict_path="empty",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) == ""

    def test_false_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            dict_path="false",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) is False

    def test_search_for_false_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            search_query="false",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) == [False]

    @pytest.mark.xfail(reason="The dictor library bug")
    def test_search_for_null_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            search_query="none",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) == [None]

    def test_search_for_empty_string_value(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(
            comparer=is_equal_comparer,
            expected_value=None,
            search_query="empty",
            dictor_fallback="Nope",
        )
        assert checker.prepare_data(example_response) == [""]

    def test_search_for_nested_value_without_path(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
    ):
        checker = JsonChecker(is_equal_comparer, None, search_query="name")
        assert checker.prepare_data(example_response) == ["John", "Mike", "Jack"]

    def test_prepare_data_catch_json_decode_error(
        self,
        mocker: MockerFixture,
        caplog: LogCaptureFixture,
        is_equal_comparer: Callable[[Any, Any], bool],
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
                10,
                "Check uuid: None | Response content: b'{ \"name'",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                40,
                "Check uuid: None | Expected: TEST"
                " | Headers: {'error': 'JSONDecodeError'} | Content b'{ \"name'",
            ),
        ]

        data = JsonChecker(
            comparer=is_equal_comparer, expected_value="TEST", search_query="name"
        ).prepare_data(response)
        assert data is None
        assert caplog.record_tuples == logs

    def test_prepare_data_catch_type_error(
        self,
        mocker: MockerFixture,
        caplog: LogCaptureFixture,
        is_equal_comparer: Callable[[Any, Any], bool],
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
                10,
                "Check uuid: None | Response content: b'{ \"name'",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                40,
                "Check uuid: None | Expected: TEST | Headers: {'error': 'TypeError'} | "
                "Content b'{ \"name'",
            ),
        ]

        data = JsonChecker(
            comparer=is_equal_comparer, expected_value="TEST", search_query="name"
        ).prepare_data(response)
        assert data is None
        assert caplog.record_tuples == logs


class TestHeadersChecker:
    def test_str(self, is_equal_comparer: Callable[[Any, Any], bool]):
        checker = HeadersChecker(is_equal_comparer, 5)
        msg = (
            "Checker: HeadersChecker | Comparer: comparer | Dictor_fallback: None |"
            " Expected_value: 5 | Path: None | Search_query: None | Data: None"
        )

        assert str(checker) == msg

    def test_dict(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("uuid.uuid4", lambda: "TestHeadersChecker")
        checker = HeadersChecker(
            comparer=is_equal_comparer, expected_value="WebLudus.pl", dict_path="Server"
        )
        logs = [
            (
                "bepatient.waiter_src.checker",
                20,
                "Check uuid: TestHeadersChecker | Checker: HeadersChecker"
                " | Comparer: comparer | Dictor_fallback: None"
                " | Expected_value: WebLudus.pl | Path: Server | Search_query: None"
                " | Data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Response headers:"
                " {'Content-Language': 'en-US', 'Content-Type': 'application/json',"
                " 'Server': 'WebLudus.pl', 'X-Render-Origin_Server': 'gunicorn'}",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Dictor path: Server"
                " | Dictor search: None | Dictor data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checker",
                10,
                "Check success! | uuid: TestHeadersChecker | Checker: HeadersChecker"
                " | Comparer: comparer | Dictor_fallback: None"
                " | Expected_value: WebLudus.pl | Path: Server | Search_query: None"
                " | Data: WebLudus.pl",
            ),
        ]
        assert checker.check(example_response) is True
        assert caplog.record_tuples == logs

    def test_search_query(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ) -> None:
        checker = HeadersChecker(
            comparer=is_equal_comparer,
            expected_value=["application/json"],
            search_query="Content-Type",
        )
        assert checker.check(example_response) is True

    def test_condition_not_met(
        self,
        is_equal_comparer: Callable[[Any, Any], bool],
        example_response: Response,
        caplog: LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("uuid.uuid4", lambda: "TestHeadersChecker")
        checker = HeadersChecker(
            comparer=is_equal_comparer, expected_value="example.com", dict_path="Server"
        )
        logs = [
            (
                "bepatient.waiter_src.checker",
                20,
                "Check uuid: TestHeadersChecker | Checker: HeadersChecker"
                " | Comparer: comparer | Dictor_fallback: None"
                " | Expected_value: example.com | Path: Server | Search_query: None"
                " | Data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Response headers:"
                " {'Content-Language': 'en-US', 'Content-Type': 'application/json',"
                " 'Server': 'WebLudus.pl', 'X-Render-Origin_Server': 'gunicorn'}",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                20,
                "Check uuid: TestHeadersChecker | Dictor path: Server"
                " | Dictor search: None | Dictor data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checker",
                20,
                "Check uuid: TestHeadersChecker | Condition not met"
                " | Checker: HeadersChecker | Comparer: comparer"
                " | Dictor_fallback: None | Expected_value: example.com"
                " | Path: Server | Search_query: None | Data: WebLudus.pl",
            ),
        ]
        assert checker.check(example_response) is False
        assert caplog.record_tuples == logs

    def test_missing_key(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = HeadersChecker(
            comparer=is_equal_comparer, expected_value="TEST", dict_path="status"
        )
        assert checker.check(example_response) is False

    def test_missing_in_search_query(
        self, is_equal_comparer: Callable[[Any, Any], bool], example_response: Response
    ):
        checker = HeadersChecker(
            comparer=is_equal_comparer, expected_value="TEST", search_query="name"
        )
        assert checker.check(example_response) is False
