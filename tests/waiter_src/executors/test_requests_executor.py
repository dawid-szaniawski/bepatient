from typing import Any, Callable

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from requests import PreparedRequest, RequestException, Response, Session

from bepatient.waiter_src.checker import Checker
from bepatient.waiter_src.exceptions.executor_exceptions import ExecutorIsNotReady
from bepatient.waiter_src.executors.requests_executor import RequestsExecutor


class TestRequestExecutor:
    def test_executor_returns_true_for_expected_status_code(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
    ):
        executor = RequestsExecutor(
            prepared_request, expected_status_code=200, session=session_mock
        )
        assert executor.is_condition_met() is True

    def test_is_condition_met_returns_true_when_checker_pass(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=200
        ).add_checker(checker_true)

        assert executor.is_condition_met() is True

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
            .add_checker(checker_true)
            .add_checker(checker_true)
        )

        assert executor.is_condition_met() is True

    def test_is_condition_met_returns_false_when_checker_fail(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_false: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session_mock
        ).add_checker(checker_false)

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
            .add_checker(checker_false)
            .add_checker(checker_true)
        )

        assert executor.is_condition_met() is False

    def test_is_condition_met_returns_false_when_status_code_check_fail(
        self,
        prepared_request: PreparedRequest,
        mocker: MockerFixture,
        checker_true: Checker,
    ):
        session = mocker.MagicMock()
        response = mocker.MagicMock()
        response.status_code = 404
        session.send.return_value = response
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session
        ).add_checker(checker_true)

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

    def test_get_result_returns_response(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        dict_content_response: Response,
        checker_true: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=200
        ).add_checker(checker_true)

        executor.is_condition_met()
        result = executor.get_result()

        assert result == dict_content_response

    def test_error_message_returns_correct_message_status_checker(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=404
        ).add_checker(checker_true)

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met! | Failed checkers:"
            " (Checker: StatusCodeChecker | Comparer: is_equal"
            " | Expected_value: 404 | Data: 200)"
            " | curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
            "https://webludus.pl/"
        )

    def test_error_message_returns_correct_message_normal_checker(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_false: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=200
        ).add_checker(checker_false)

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met!"
            " | Failed checkers: (I'm falsy) | curl -X GET -H 'task: test'"
            " -H 'Cookie: user-token=abc-123' https://webludus.pl/"
        )

    def test_error_message_returns_correct_message_multiple_checkers(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_false: Checker,
        is_equal: Callable[[Any, Any], bool],
    ):
        class CheckerMocker(Checker):
            def __str__(self) -> str:
                return "I'm even more falsy"

            def prepare_data(self, data: Any, run_uuid: str | None = None) -> None:
                """mock"""

            def check(self, data: Any) -> bool:
                return False

        executor = (
            RequestsExecutor(
                req_or_res=prepared_request,
                session=session_mock,
                expected_status_code=200,
            )
            .add_checker(checker_false)
            .add_checker(CheckerMocker(is_equal, ""))
            .add_checker(checker_false)
        )

        executor.is_condition_met()

        assert executor.error_message() == (
            "The condition has not been met!"
            " | Failed checkers: (I'm falsy, I'm even more falsy, I'm falsy)"
            " | curl -X GET -H 'task: test'"
            " -H 'Cookie: user-token=abc-123' https://webludus.pl/"
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
        prepared_request: PreparedRequest,
        session_mock: Session,
        checker_true: Checker,
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, session=session_mock, expected_status_code=200
        ).add_checker(checker_true)

        executor.is_condition_met()

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
            timeout=1
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
                20,
                "Creating a new Session object",
            )
        ]

        assert isinstance(executor.session, Session)
        assert caplog.record_tuples == logs

    def test_response_headers_merged_into_session(
        self,
        dict_content_response: Response,
        prepared_request: PreparedRequest,
        caplog: LogCaptureFixture,
    ):
        dict_content_response.request = prepared_request
        session = Session()
        session.headers = {"test_name": "test_response_headers_merged_into_session"}
        expected_headers = session.headers | dict(prepared_request.headers)
        logs = [
            (
                "bepatient.waiter_src.executors.requests_executor",
                20,
                "Merging response data into session",
            )
        ]

        executor = RequestsExecutor(
            req_or_res=dict_content_response, expected_status_code=200, session=session
        )

        assert executor.session.headers == expected_headers
        assert caplog.record_tuples == logs

    def test_self_request_is_first_response_request(
        self, dict_content_response: Response, prepared_request: PreparedRequest
    ):
        dict_content_response.request = prepared_request

        executor = RequestsExecutor(
            req_or_res=dict_content_response, expected_status_code=200
        )

        assert executor.request == prepared_request

    def test_self_request_is_first_request_from_history(
        self,
        dict_content_response: Response,
        headers_response: Response,
        prepared_request: PreparedRequest,
    ):
        additional_response = Response()
        additional_response.request = prepared_request
        dict_content_response.history = [additional_response, headers_response]

        dict_content_response.request = PreparedRequest()
        dict_content_response.request.prepare_headers({})

        executor = RequestsExecutor(
            req_or_res=dict_content_response, expected_status_code=200
        )

        assert executor.request == prepared_request

    def test_set_5s_timeout_if_timeout_not_provided(self, prepared_request):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200
        )

        assert executor.timeout == 5
