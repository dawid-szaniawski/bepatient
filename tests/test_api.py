import json
from typing import Any

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from requests import PreparedRequest, Request, Response, Session
from responses import RequestsMock

from bepatient import (
    RequestsWaiter,
    dict_differences,
    to_curl,
    wait_for_value_in_request,
    wait_for_values_in_request,
)
from bepatient.waiter_src.checkers.response_checkers import HeadersChecker
from bepatient.waiter_src.comparators import is_equal
from bepatient.waiter_src.exceptions.waiter_exceptions import WaiterConditionWasNotMet


class TestRequestsWaiter:
    def test_init(self, prepared_request: PreparedRequest, session_mock: Session):
        executor = RequestsWaiter(
            request=prepared_request, status_code=201, session=session_mock
        ).executor

        assert executor.request == prepared_request
        assert executor.session is session_mock

        checker = executor._status_code_checker
        assert checker.expected_value == 201

    def test_add_checker(self, prepared_request: PreparedRequest):
        waiter = RequestsWaiter(request=prepared_request)
        executor = waiter.add_checker(
            expected_value="TEST",
            comparer="is_equal",
            checker="headers_checker",
            dict_path="dict",
            search_query="search",
        ).executor

        checker = HeadersChecker(
            comparer=is_equal,
            expected_value="TEST",
            dict_path="dict",
            search_query="search",
        )

        assert executor._checkers[0].__dict__ == checker.__dict__

    def test_add_custom_checker(self, prepared_request: PreparedRequest):
        checker = HeadersChecker(isinstance, dict)
        waiter = RequestsWaiter(request=prepared_request)
        executor = waiter.add_custom_checker(checker).executor
        w_checker = executor._checkers[0]

        assert w_checker is checker

    def test_happy_path_prepared_request(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=True, comparer="is_equal", dict_path="ok")
        response = waiter.run(retries=1).get_result()

        assert response == example_response

    def test_happy_path_request(
        self,
        mocked_responses: RequestsMock,
        request_object: Request,
        example_dict_content: dict[str, Any],
        mocker: MockerFixture,
        session_object: Session,
        caplog: LogCaptureFixture,
    ):
        mocked_responses.get(request_object.url, status=404)
        mocked_responses.get(request_object.url, status=200)
        mocked_responses.get(
            request_object.url,
            status=200,
            body=json.dumps(example_dict_content).encode("utf-8"),
        )
        mocker.patch("uuid.uuid4", side_effect=[1, 2, 3])
        logs = [
            (
                "bepatient.waiter_src.waiter",
                20,
                "Checking whether the condition has been met. The 1 approach",
            ),
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Sent: curl -X GET -H 'Content-Type: application/json'"
                " -H 'Accept-Language: en-US,en;' -H 'Host: webludus.pl'"
                " -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:120.0)"
                " Gecko/20100101' -H 'task: test' -H 'Cookie: pytest=fixture;"
                " user-token=abc-123' https://webludus.pl/",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: 1 | Checker: StatusCodeChecker | Comparer: is_equal | "
                "Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: 1 | Response status code: 404 | Response content: b''",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check uuid: 1 | Condition not met | Checker: StatusCodeChecker"
                " | Comparer: is_equal | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "The condition has not been met. Waiting time: 1",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "Checking whether the condition has been met. The 2 approach",
            ),
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Sent: curl -X GET -H 'Content-Type: application/json'"
                " -H 'Accept-Language: en-US,en;' -H 'Host: webludus.pl'"
                " -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:120.0)"
                " Gecko/20100101' -H 'task: test' -H 'Cookie: pytest=fixture;"
                " user-token=abc-123' https://webludus.pl/",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: 2 | Checker: StatusCodeChecker | Comparer: is_equal"
                " | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: 2 | Response status code: 200 | Response content: b''",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: 2 | Checker: StatusCodeChecker"
                " | Comparer: is_equal | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: 2 | Checker: JsonChecker | Comparer: is_equal | "
                "Dictor_fallback: None | Expected_value: Jack | Ignore_case: False"
                " | Path: name | Search_query: None | Data: Jack",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: 2 | Response content: b''",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                40,
                "Check uuid: 2 | Expected: Jack | Headers: {'Content-Type':"
                " 'text/plain'} | Content b''",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check uuid: 2 | Condition not met | Checker: JsonChecker"
                " | Comparer: is_equal | Dictor_fallback: None | Expected_value: Jack"
                " | Ignore_case: False | Path: name | Search_query: None | Data: Jack",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "The condition has not been met. Waiting time: 1",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "Checking whether the condition has been met. The 3 approach",
            ),
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Sent: curl -X GET -H 'Content-Type: application/json'"
                " -H 'Accept-Language: en-US,en;' -H 'Host: webludus.pl'"
                " -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:120.0)"
                " Gecko/20100101' -H 'task: test' -H 'Cookie: pytest=fixture;"
                " user-token=abc-123' https://webludus.pl/",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: 3 | Checker: StatusCodeChecker | Comparer: is_equal | "
                "Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: 3 | Response status code: 200 | Response content: "
                'b\'{"list_of_dicts": [{"name": "John", "age": 30}, {"name": "Mike",'
                ' "age": 15}], "ok": true, "some_number": 123, "list": ["1", "2", "3"],'
                ' "none": null, "empty": "", "false": false, "name": "Jack", "City":'
                ' "Cracow"}\'',
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: 3 | Checker: StatusCodeChecker"
                " | Comparer: is_equal | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: 3 | Checker: JsonChecker | Comparer: is_equal"
                " | Dictor_fallback: None | Expected_value: Jack | Ignore_case: False"
                " | Path: name | Search_query: None | Data: Jack",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                'Check uuid: 3 | Response content: b\'{"list_of_dicts": [{"name":'
                ' "John", "age": 30}, {"name": "Mike", "age": 15}], "ok": true,'
                ' "some_number": 123, "list": ["1", "2", "3"], "none": null, "empty":'
                ' "", "false": false, "name": "Jack", "City": "Cracow"}\'',
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: 3 | Dictor path: name | Dictor search: None"
                " | Dictor data: Jack",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: 3 | Checker: JsonChecker | Comparer: is_equal"
                " | Dictor_fallback: None | Expected_value: Jack | Ignore_case: False"
                " | Path: name | Search_query: None | Data: Jack",
            ),
            ("bepatient.waiter_src.waiter", 20, "Condition met!"),
        ]

        waiter = RequestsWaiter(request=request_object, session=session_object)
        waiter.add_checker(expected_value="Jack", comparer="is_equal", dict_path="name")
        res_json = waiter.run(retries=3).get_result().json()

        mocked_responses.assert_call_count(url=request_object.url, count=3)
        assert res_json == example_dict_content
        assert caplog.record_tuples == logs

    def test_happy_path(
        self,
        mocked_responses: RequestsMock,
        example_dict_content: dict[str, Any],
        prepared_request: PreparedRequest,
        session_object: Session,
    ):
        res = Response()
        res.status_code = 404
        res.request = prepared_request

        mocked_responses.get(
            res.request.url, status=200, headers={"Content-Type": "application/json"}
        )
        mocked_responses.get(
            res.request.url,
            status=200,
            headers={"Content-Type": "application/json", "Server": "WebLudus.pl"},
            body=json.dumps(example_dict_content).encode("utf-8"),
        )

        waiter = RequestsWaiter(request=res, session=session_object)
        waiter.add_checker(
            expected_value="WebLudus.pl",
            comparer="is_equal",
            checker="headers_checker",
            dict_path="Server",
        )
        error_message = (
            "The condition has not been met!"
            " | Failed checkers: (Checker: HeadersChecker | Comparer: is_equal"
            " | Dictor_fallback: None | Expected_value: WebLudus.pl"
            " | Ignore_case: False | Path: Server | Search_query: None | Data: None)"
            " | curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123;"
            " pytest=fixture' -H 'Content-Type: application/json' -H 'Accept-Language:"
            " en-US,en;' -H 'Host: webludus.pl' -H 'User-Agent: Mozilla/5.0"
            " (Windows NT 10.0; rv:120.0) Gecko/20100101' https://webludus.pl/"
        )
        with pytest.raises(WaiterConditionWasNotMet, match=error_message):
            waiter.run(retries=2)
        res_json = waiter.run(retries=1).get_result().json()

        mocked_responses.assert_call_count(url=res.request.url, count=2)  # type: ignore
        assert res_json == example_dict_content

    def test_happy_path_with_custom_checker(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        checker = HeadersChecker(
            comparer=isinstance, expected_value=str, dict_path="Server"
        )
        waiter.add_custom_checker(checker)
        response = waiter.run(retries=1).get_result()

        assert response == example_response
        assert response.headers["Content-Type"] == "application/json"

    def test_condition_not_met_raise_error(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
        error_msg: str,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=False, comparer="is_equal", dict_path="ok")
        with pytest.raises(WaiterConditionWasNotMet, match=error_msg):
            waiter.run(retries=1)

        assert waiter.get_result() == example_response

    def test_condition_not_met_without_error(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=False, comparer="is_equal", dict_path="ok")
        waiter.run(retries=1, raise_error=False)

        assert waiter.get_result() == example_response

    def test_wait_for_value(
        self,
        mocker: MockerFixture,
        prepared_request: PreparedRequest,
        example_response: Response,
        caplog: LogCaptureFixture,
    ):
        res = Response()
        res.status_code = 200
        res.request = prepared_request
        mocker.patch("uuid.uuid4", side_effect=["TEST1", "TEST2"])
        mocker.patch(
            "requests.Session.send",
            side_effect=[res, example_response],
        )
        logs = [
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Creating a new Session object",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "Checking whether the condition has been met. The 1 approach",
            ),
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Sent: curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123'"
                " https://webludus.pl/",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: TEST1 | Checker: StatusCodeChecker | Comparer: is_equal"
                " | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST1 | Response status code: 200"
                " | Response content: None",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: TEST1 | Checker: StatusCodeChecker"
                " | Comparer: is_equal | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: TEST1 | Checker: HeadersChecker | Comparer: is_equal"
                " | Dictor_fallback: None | Expected_value: WebLudus.pl"
                " | Ignore_case: False | Path: Server | Search_query: None"
                " | Data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST1 | Response headers: {}",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST1 | Dictor path: Server | Dictor search: None"
                " | Dictor data: None",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check uuid: TEST1 | Condition not met | Checker: HeadersChecker"
                " | Comparer: is_equal | Dictor_fallback: None"
                " | Expected_value: WebLudus.pl | Ignore_case: False | Path: Server"
                " | Search_query: None | Data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "The condition has not been met. Waiting time: 1",
            ),
            (
                "bepatient.waiter_src.waiter",
                20,
                "Checking whether the condition has been met. The 2 approach",
            ),
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Sent: curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
                "https://webludus.pl/",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: TEST2 | Checker: StatusCodeChecker | Comparer: is_equal"
                " | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST2 | Response status code: 200 | Response content:"
                ' b\'{"list_of_dicts": [{"name": "John", "age": 30}, {"name": "Mike",'
                ' "age": 15}], "ok": true, "some_number": 123, "list": ["1", "2", "3"],'
                ' "none": null, "empty": "", "false": false, "name": "Jack",'
                ' "City": "Cracow"}\'',
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: TEST2 | Checker: StatusCodeChecker | Comparer:"
                " is_equal | Expected_value: 200 | Data: 200",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                10,
                "Check uuid: TEST2 | Checker: HeadersChecker | Comparer: is_equal"
                " | Dictor_fallback: None | Expected_value: WebLudus.pl"
                " | Ignore_case: False | Path: Server | Search_query: None"
                " | Data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST2 | Response headers: {'Content-Language': 'en-US',"
                " 'Content-Type': 'application/json', 'Server': 'WebLudus.pl',"
                " 'X-Render-Origin_Server': 'gunicorn'}",
            ),
            (
                "bepatient.waiter_src.checkers.response_checkers",
                10,
                "Check uuid: TEST2 | Dictor path: Server | Dictor search: None"
                " | Dictor data: WebLudus.pl",
            ),
            (
                "bepatient.waiter_src.checkers.checker",
                20,
                "Check success! | uuid: TEST2 | Checker: HeadersChecker"
                " | Comparer: is_equal | Dictor_fallback: None"
                " | Expected_value: WebLudus.pl | Ignore_case: False | Path: Server"
                " | Search_query: None | Data: WebLudus.pl",
            ),
            ("bepatient.waiter_src.waiter", 20, "Condition met!"),
        ]

        waiter = RequestsWaiter(request=prepared_request)
        waiter.add_checker(
            expected_value="WebLudus.pl",
            comparer="is_equal",
            checker="headers_checker",
            dict_path="Server",
        )
        waiter.run(retries=2)

        assert waiter.get_result() == example_response
        assert caplog.record_tuples == logs


class TestWaitForValueInRequests:
    def test_happy_path(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
    ):
        result = wait_for_value_in_request(
            request=prepared_request,
            session=session_mock,
            comparer="is_equal",
            expected_value=True,
            dict_path="ok",
            retries=1,
        )

        assert result == example_response

    def test_condition_not_met_raise_error(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        error_msg: str,
    ):
        with pytest.raises(WaiterConditionWasNotMet, match=error_msg):
            wait_for_value_in_request(
                request=prepared_request,
                session=session_mock,
                comparer="is_equal",
                expected_value=False,
                dict_path="ok",
                retries=1,
            )


class TestWaitForValuesInRequests:
    def test_happy_path(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        example_response: Response,
    ):
        list_of_checkers = [
            {
                "checker": "json_checker",
                "comparer": "contain",
                "expected_value": "John",
                "dict_path": "list_of_dicts",
                "search_query": "name",
            },
            {
                "checker": "headers_checker",
                "comparer": "is_equal",
                "expected_value": "en-US",
                "dict_path": "Content-Language",
            },
        ]

        response = wait_for_values_in_request(
            request=prepared_request,
            session=session_mock,
            checkers=list_of_checkers,
            retries=1,
        )

        assert response == example_response

    def test_condition_not_met_raise_error(
        self, prepared_request: PreparedRequest, session_mock: Session
    ):
        msg = (
            "The condition has not been met! | Failed checkers:"
            " (Checker: JsonChecker | Comparer: contain | Dictor_fallback: None"
            " | Expected_value: Jerry | Path: list_of_dicts | Search_query: name"
            " | Data: ['John', 'Mike'], Checker: HeadersChecker | Comparer: is_equal"
            " | Dictor_fallback: None | Expected_value: xml | Path: content"
            " | Search_query: None | Data: json) | curl -X GET -H 'task: test' -H"
            " 'Cookie: user-token=abc-123' https://webludus.pl/"
        )
        list_of_checkers = [
            {
                "checker": "json_checker",
                "comparer": "contain",
                "expected_value": "Jerry",
                "dict_path": "list_of_dicts",
                "search_query": "name",
            },
            {
                "checker": "headers_checker",
                "comparer": "is_equal",
                "expected_value": "xml",
                "dict_path": "content",
            },
        ]

        with pytest.raises(WaiterConditionWasNotMet, match=msg):
            wait_for_values_in_request(
                request=prepared_request,
                session=session_mock,
                checkers=list_of_checkers,
                retries=1,
            )


def test_dict_differences():
    expected_dict = {
        "Key1": 1,
        "Key2": None,
        "Key3": "STRING",
        "Key4": "Another string",
    }
    actual_dict = {"Key1": 2, "Key5": False, "Key3": "STRING", "1": True}
    msg = {
        "key_missing_exp": {"Key2", "Key4"},
        "key_missing_actual": {"Key5", "1"},
        "value_diff": {"Key1": {"expected": 1, "actual": 2}},
    }
    assert dict_differences(expected_dict=expected_dict, actual_dict=actual_dict) == msg


def test_to_curl(prepared_request: PreparedRequest):
    expected_curl = (
        "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
        "https://webludus.pl/"
    )

    assert to_curl(prepared_request) == expected_curl
