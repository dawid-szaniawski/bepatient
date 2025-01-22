import json
from typing import Any, Callable

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from requests import PreparedRequest, Request, RequestException, Response, Session
from responses import RequestsMock

from bepatient.waiter_src.checkers.checker import Checker
from bepatient.waiter_src.exceptions import ExceptionConditionNotMet, ExecutorIsNotReady
from bepatient.waiter_src.executors.requests_executor import RequestsExecutor


class TestRequestExecutor:
    def test_proper_headers_cookies_from_request(
        self,
        mocked_responses: RequestsMock,
        example_dict_content: dict[str, Any],
        session_object: Session,
        request_object: Request,
    ):
        res_mock = mocked_responses.get(
            request_object.url,
            status=200,
            body=json.dumps(example_dict_content).encode("utf-8"),
        )
        executor = RequestsExecutor(
            req_or_res=request_object,
            expected_status_code=200,
            session=session_object,
        )
        expected_request_headers = {
            **session_object.headers,
            **request_object.headers,
            "Cookie": "pytest=fixture; user-token=abc-123",
        }

        assert executor.is_condition_met()
        assert res_mock.call_count == 1
        assert executor.get_result().json() == example_dict_content
        assert executor.get_result().request.headers == expected_request_headers

    @pytest.mark.parametrize(
        "fixture_name, expected_cookies, additional_log",
        [
            (
                "example_response",
                {"Cookie": "user-token=abc-123; pytest=fixture"},
                "PreparedRequest already has cookies.",
            ),
            ("response_without_cookies_in_request", {"Cookie": "pytest=fixture"}, None),
        ],
    )
    def test_proper_headers_cookies_from_response(
        self,
        mocked_responses: RequestsMock,
        request: FixtureRequest,
        session_object: Session,
        fixture_name: str,
        expected_cookies: dict[str, str],
        additional_log: str,
        caplog: LogCaptureFixture,
    ):
        response = request.getfixturevalue(fixture_name)
        response.status_code = 404
        res_mock = mocked_responses.get(
            response.request.url,
            status=200,
        )
        executor = RequestsExecutor(
            req_or_res=response,
            expected_status_code=200,
            session=session_object,
        )
        expected_request_headers = {
            **response.request.headers,
            **session_object.headers,
            **expected_cookies,
        }

        assert "Merging session.headers into PreparedRequest object" in caplog.text
        assert "Merging session.cookies into PreparedRequest object" in caplog.text
        if additional_log:
            assert "PreparedRequest already has cookies" in caplog.text
        assert not executor.is_condition_met()
        assert executor.is_condition_met()
        assert res_mock.call_count == 1
        assert executor.get_result().request.headers == expected_request_headers

    def test_is_condition_met_returns_true_when_checker_pass(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=200
        ).add_main_condition(checker_true)

        assert executor.is_condition_met()

    def test_is_condition_met_returns_true_when_all_checkers_pass(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
    ):
        executor = (
            RequestsExecutor(
                req_or_res=prepared_request,
                expected_status_code=200,
                session=session_mock,
            )
            .add_main_condition(checker_true)
            .add_main_condition(checker_true)
            .add_pre_condition(checker_true)
            .add_exception_condition(checker_true)
        )

        assert executor.is_condition_met()

    def test_is_condition_met_returns_false_when_checker_fail(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_false: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session_mock
        ).add_main_condition(checker_false)

        assert executor.is_condition_met() is False

    def test_is_condition_met_returns_false_when_not_all_checkers_pass(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
        checker_false: Checker,
    ):
        executor = (
            RequestsExecutor(
                req_or_res=prepared_request,
                expected_status_code=200,
                session=session_mock,
            )
            .add_main_condition(checker_false)
            .add_main_condition(checker_true)
        )

        assert executor.is_condition_met() is False

    def test_is_condition_met_returns_false_when_status_code_check_fail(
        self,
        prepared_request: PreparedRequest,
        example_response: Response,
        mocker: MockerFixture,
        checker_true: Checker,
    ):
        session = mocker.MagicMock()
        response = example_response
        response.status_code = 404
        session.send.return_value = response
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session
        ).add_main_condition(checker_true)

        assert executor.is_condition_met() is False

    def test_get_result_raises_exception_when_condition_has_not_been_checked(
        self, prepared_request: PreparedRequest, session_mock: Session
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session_mock
        )

        msg = "The condition has not yet been checked."
        with pytest.raises(ExecutorIsNotReady, match=msg):
            executor.get_result()

    def test_error_message_returns_correct_message_status_checker(
        self,
        mocked_responses: RequestsMock,
        request_object: Request,
        session_object: Session,
        checker_true: Checker,
    ):
        mocked_responses.get(request_object.url, status=200)
        executor = RequestsExecutor(
            req_or_res=request_object, session=session_object, expected_status_code=404
        ).add_main_condition(checker_true)

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers:"
            " (Checker: StatusCodeChecker | Comparer: is_equal | Expected_value: 404"
            " | Data: 200) | curl -X GET -H 'Content-Type: application/json'"
            " -H 'Accept-Language: en-US,en;' -H 'Host: webludus.pl'"
            " -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101'"
            " -H 'task: test' -H 'Cookie: pytest=fixture; user-token=abc-123'"
            " https://webludus.pl/"
        )

    def test_error_message_returns_correct_message_normal_checker(
        self,
        mocked_responses: RequestsMock,
        request_object: Request,
        session_object: Session,
        checker_false: Checker,
    ):
        mocked_responses.get(request_object.url, status=200)
        executor = RequestsExecutor(
            req_or_res=request_object, session=session_object, expected_status_code=200
        ).add_main_condition(checker_false)

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers: (Checker: CheckerMocker"
            " | Comparer: comparer | Expected_value: TEST | Data: Ok)"
            " | curl -X GET -H 'Content-Type: application/json' -H 'Accept-Language:"
            " en-US,en;' -H 'Host: webludus.pl' -H 'User-Agent: Mozilla/5.0"
            " (Windows NT 10.0; rv:120.0) Gecko/20100101' -H 'task: test' -H 'Cookie:"
            " pytest=fixture; user-token=abc-123' https://webludus.pl/"
        )

    def test_error_message_returns_correct_message_multiple_checkers(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_false: Checker,
        is_equal_comparer: Callable[[Any, Any], bool],
    ):
        class AnotherChecker(Checker):
            def prepare_data(self, data: Any, run_uuid: str | None = None) -> str:
                return "MOCK"

        executor = (
            RequestsExecutor(
                req_or_res=prepared_request,
                session=session_mock,
                expected_status_code=200,
            )
            .add_main_condition(checker_false)
            .add_main_condition(AnotherChecker(is_equal_comparer, "Hello"))
            .add_main_condition(checker_false)
        )

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers: (Checker: CheckerMocker"
            " | Comparer: comparer | Expected_value: TEST | Data: Ok, Checker:"
            " AnotherChecker | Comparer: comparer | Expected_value: Hello"
            " | Data: MOCK, Checker: CheckerMocker | Comparer: comparer"
            " | Expected_value: TEST | Data: Ok) | curl -X GET -H 'task: test' -H"
            " 'Cookie: user-token=abc-123' https://webludus.pl/"
        )

    def test_error_message_raises_exception_when_condition_has_not_been_checked(
        self, prepared_request: PreparedRequest, session_mock: Session
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session_mock
        )

        msg = "The condition has not yet been checked."
        with pytest.raises(ExecutorIsNotReady, match=msg):
            executor.error_message()

    def test_condition_met_error_message(
        self,
        mocked_responses: RequestsMock,
        request_object: Request,
        session_object: Session,
        checker_true: Checker,
    ):
        res_mock = mocked_responses.get(request_object.url, status=200)
        executor = RequestsExecutor(
            req_or_res=request_object, session=session_object, expected_status_code=200
        ).add_main_condition(checker_true)

        executor.is_condition_met()

        assert res_mock.call_count == 1
        assert executor.error_message() == "All conditions have been met."

    def test_except_request_exception(
        self,
        mocker: MockerFixture,
        prepared_request: PreparedRequest,
        caplog: LogCaptureFixture,
    ):
        def error_mock(request: PreparedRequest, timeout: int):
            assert request == prepared_request
            assert timeout == 1
            raise RequestException()

        session = mocker.MagicMock()
        session.send = error_mock
        logs = [
            (
                "bepatient.waiter_src.executors.requests_executor",
                40,
                "RequestException! CURL: curl -X GET -H 'task: test' -H 'Cookie: "
                "user-token=abc-123' https://webludus.pl/",
            )
        ]

        executor = RequestsExecutor(
            req_or_res=prepared_request,
            expected_status_code=200,
            session=session,
            timeout=1,
        )

        assert executor.is_condition_met() is False
        assert caplog.record_tuples == logs

    def test_creates_own_session_if_not_provided(
        self, prepared_request: PreparedRequest, caplog: LogCaptureFixture
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200
        )
        logs = [
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Creating a new Session object",
            )
        ]

        assert isinstance(executor.session, Session)
        assert caplog.record_tuples == logs

    def test_response_headers_merged_into_session(
        self,
        example_response: Response,
        prepared_request: PreparedRequest,
        caplog: LogCaptureFixture,
    ):
        example_response.request = prepared_request
        session = Session()
        session.headers = {"test_name": "test_response_headers_merged_into_session"}
        expected_headers = dict(session.headers) | dict(prepared_request.headers)
        logs = [
            (
                "bepatient.waiter_src.executors.requests_executor",
                10,
                "Merging session.headers into PreparedRequest object",
            )
        ]

        executor = RequestsExecutor(
            req_or_res=example_response, expected_status_code=200, session=session
        )

        assert caplog.record_tuples == logs
        assert dict(executor.request.headers) == expected_headers

    def test_self_request_is_first_response_request(
        self, example_response: Response, prepared_request: PreparedRequest
    ):
        executor = RequestsExecutor(
            req_or_res=example_response, expected_status_code=200
        )

        assert executor.request == prepared_request

    def test_self_request_is_first_request_from_history(
        self,
        example_response: Response,
    ):
        expected_request = PreparedRequest()
        expected_request.prepare(method="get", url="https://example.com")

        additional_response = Response()
        additional_response.request = expected_request
        example_response.history = [additional_response, example_response]

        executor = RequestsExecutor(
            req_or_res=example_response, expected_status_code=200
        )

        assert executor.request == expected_request

    def test_set_default_timeout_if_timeout_not_provided(self, prepared_request):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200
        )

        assert executor.timeout == (15, 30)

    def test_conditions_are_checked_in_the_proper_order(
        self,
        checker_mocker: type[Checker],
        checker_true: Checker,
        example_response: Response,
        is_equal_comparer: Callable[[Any, Any], bool],
    ):
        checker_1 = checker_mocker(comparer=is_equal_comparer, expected_value=1)
        checker_2 = checker_mocker(comparer=is_equal_comparer, expected_value=2)
        checker_3 = checker_mocker(comparer=is_equal_comparer, expected_value=3)
        executor = RequestsExecutor(
            req_or_res=example_response, expected_status_code=200
        )
        executor.conditions_manager.pre_conditions = []

        executor.add_exception_condition(checker_1)
        executor.add_pre_condition(checker_2)
        executor.add_main_condition(checker_3)

        msg = (
            "Failed checkers: Checker: CheckerMocker | Comparer: comparer"
            " | Expected_value: 1 | Data: Ok"
        )
        with pytest.raises(ExceptionConditionNotMet, match=msg):
            executor.is_condition_met()

        executor.conditions_manager.exception_conditions = [checker_true]
        assert executor.is_condition_met() is False
        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers: (Checker: CheckerMocker"
            " | Comparer: comparer | Expected_value: 2 | Data: Ok) | curl -X GET -H"
            " 'task: test' -H 'Cookie: user-token=abc-123' -H 'User-Agent:"
            " python-requests/2.32.3' -H 'Accept-Encoding: gzip, deflate' -H 'Accept:"
            " */*' -H 'Connection: keep-alive' https://webludus.pl/"
        )

        executor.conditions_manager.pre_conditions = [checker_true]
        assert executor.is_condition_met() is False
        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers: (Checker: CheckerMocker"
            " | Comparer: comparer | Expected_value: 3 | Data: Ok) | curl -X GET -H"
            " 'task: test' -H 'Cookie: user-token=abc-123' -H 'User-Agent:"
            " python-requests/2.32.3' -H 'Accept-Encoding: gzip, deflate' -H 'Accept:"
            " */*' -H 'Connection: keep-alive' https://webludus.pl/"
        )

        executor.conditions_manager.main_conditions = [checker_true]
        assert executor.is_condition_met() is True
        assert executor.error_message() == "All conditions have been met."
