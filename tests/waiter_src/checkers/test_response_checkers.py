from json import JSONDecodeError
from typing import Any, Callable

from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from requests import Response

from bepatient.waiter_src.checkers.response_checkers import HeadersChecker, JsonChecker


class TestJsonChecker:
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
        msg = (
            "Expected: TEST | Headers: {'error': 'JSONDecodeError'}"
            " | Content b'{ \"name'"
        )

        data = JsonChecker(is_equal, "TEST", search_query="name").prepare_data(response)
        assert data is None
        assert msg in caplog.text


class TestHeadersChecker:
    def test_dict(
        self, headers_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = HeadersChecker(is_equal, "John", dict_path="name")
        assert checker.check(headers_response) is True

    def test_search_query(
        self, headers_response: Response, is_equal: Callable[[Any, Any], bool]
    ):
        checker = HeadersChecker(
            comparer=is_equal, expected_value=["['1', '2', '3']"], search_query="list"
        )
        assert checker.check(headers_response) is True

    def test_condition_not_met(self, headers_response: Response):
        checker = HeadersChecker(lambda a, b: b in a, "Joe", dict_path="name")
        assert checker.check(headers_response) is False

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
