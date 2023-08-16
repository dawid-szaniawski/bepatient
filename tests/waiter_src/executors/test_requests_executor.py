import pytest
from pytest_mock import MockerFixture
from requests import PreparedRequest, RequestException, Response, Session

from bepatient.waiter_src.checker import Checker
from bepatient.waiter_src.exceptions.executor_exceptions import ExecutorIsNotReady
from bepatient.waiter_src.executors.requests_executor import RequestsExecutor


class TestRequestExecutor:
    def test_executor_returns_true_for_expected_status_code(
        self, mocker: MockerFixture, session_mock: Session
    ):
        request = mocker.MagicMock()
        session = mocker.MagicMock()
        response = Response()
        response.status_code = 200
        response.json = lambda: []  # type: ignore
        session.send.return_value = response
        executor = RequestsExecutor(request, expected_status_code=200, session=session)
        assert executor.is_condition_met() is True

    def test_is_condition_met_returns_true_when_checker_pass(
        self,
        mocker: MockerFixture,
        session_mock: Session,
        checker: Checker,
    ):
        request = mocker.MagicMock()
        executor = RequestsExecutor(
            req_or_res=request, session=session_mock, expected_status_code=200
        ).add_checker(checker)

        is_met = executor.is_condition_met()

        assert is_met is True

    def test_is_condition_met_returns_true_when_all_checkers_pass(
        self, mocker: MockerFixture, session_mock: Session, checker: Checker
    ):
        request = mocker.MagicMock()
        executor = (
            RequestsExecutor(
                req_or_res=request, expected_status_code=200, session=session_mock
            )
            .add_checker(checker)
            .add_checker(checker)
        )

        is_met = executor.is_condition_met()

        assert is_met is True

    def test_is_condition_met_returns_false_when_checker_fail(
        self, mocker: MockerFixture, session_mock: Session, checker_false: Checker
    ):
        request = mocker.MagicMock()
        executor = RequestsExecutor(
            req_or_res=request, expected_status_code=200, session=session_mock
        ).add_checker(checker_false)

        is_met = executor.is_condition_met()

        assert is_met is False

    def test_is_condition_met_returns_false_when_not_all_checkers_pass(
        self,
        mocker: MockerFixture,
        session_mock: Session,
        checker: Checker,
        checker_false: Checker,
    ):
        request = mocker.MagicMock()
        executor = (
            RequestsExecutor(
                req_or_res=request, expected_status_code=200, session=session_mock
            )
            .add_checker(checker_false)
            .add_checker(checker)
        )

        is_met = executor.is_condition_met()

        assert is_met is False

    def test_is_condition_met_returns_false_when_status_code_check_fail(
        self, mocker: MockerFixture, checker: Checker
    ):
        request = mocker.MagicMock()
        session = mocker.MagicMock()
        response = Response()
        response.status_code = 404
        response.json = lambda: []  # type: ignore
        session.send.return_value = response
        executor = RequestsExecutor(
            req_or_res=request, expected_status_code=200, session=session
        ).add_checker(checker)

        is_met = executor.is_condition_met()

        assert is_met is False

    def test_get_result_raises_exception_when_condition_has_not_been_checked(
        self, mocker: MockerFixture, session_mock: Session
    ):
        request = mocker.MagicMock()
        executor = RequestsExecutor(
            req_or_res=request, expected_status_code=200, session=session_mock
        )

        msg = "The condition has not yet been checked."
        with pytest.raises(ExecutorIsNotReady, match=msg):
            executor.get_result()

    def test_get_result_returns_response(
        self,
        mocker: MockerFixture,
        session_mock: Session,
        response: Response,
        checker: Checker,
    ):
        request = mocker.MagicMock()
        executor = RequestsExecutor(
            req_or_res=request, session=session_mock, expected_status_code=200
        ).add_checker(checker)

        executor.is_condition_met()
        result = executor.get_result()

        assert result == response

    def test_error_message_returns_correct_message_status_checker(
        self, prepared_request: PreparedRequest, mocker: MockerFixture, checker: Checker
    ):
        request = prepared_request
        session = mocker.MagicMock()
        response = Response()
        response.status_code = 404
        response.url = "https://webludus.pl"
        response._content = b'{"error": "not found"}'
        session.send.return_value = response
        executor = RequestsExecutor(
            req_or_res=request, session=session, expected_status_code=200
        ).add_checker(checker)

        executor.is_condition_met()
        error_message = executor.error_message()

        assert error_message == (
            "The condition has not been met! | Failed checkers: (Checker:"
            " StatusCodeChecker | Comparer: is_equal | Expected_value: 200 | Data: 404)"
            " | curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123'"
            " https://webludus.pl/"
        )

    def test_error_message_returns_correct_message_normal_checker(
        self,
        prepared_request: PreparedRequest,
        mocker: MockerFixture,
        checker_false: Checker,
    ):
        request = prepared_request
        session = mocker.MagicMock()
        response = Response()
        response.status_code = 200
        response.url = "https://webludus.pl"
        response._content = b'{"error": "not found"}'
        session.send.return_value = response
        executor = RequestsExecutor(
            req_or_res=request, session=session, expected_status_code=200
        ).add_checker(checker_false)

        executor.is_condition_met()
        error_message = executor.error_message()

        assert error_message == (
            "The condition has not been met!"
            " | Failed checkers: (I'm falsy) | curl -X GET -H 'task: test'"
            " -H 'Cookie: user-token=abc-123' https://webludus.pl/"
        )

    def test_error_message_raises_exception_when_condition_has_not_been_checked(
        self, mocker: MockerFixture, session_mock: Session
    ):
        request = mocker.MagicMock()
        executor = RequestsExecutor(
            req_or_res=request, expected_status_code=200, session=session_mock
        )

        msg = "The condition has not yet been checked."
        with pytest.raises(ExecutorIsNotReady, match=msg):
            executor.error_message()

    def test_except_request_exception(
        self, mocker: MockerFixture, prepared_request: PreparedRequest
    ):
        def error_mock(_: PreparedRequest):
            raise RequestException()

        session = mocker.MagicMock()
        session.send = error_mock

        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200, session=session
        )

        assert executor.is_condition_met() is False

    def test_creates_own_session_if_not_provided(
        self, prepared_request: PreparedRequest
    ):
        executor = RequestsExecutor(
            req_or_res=prepared_request, expected_status_code=200
        )

        assert isinstance(executor.session, Session)

    def test_response_headers_merged_into_session(
        self, response: Response, prepared_request: PreparedRequest
    ):
        response.request = prepared_request
        session = Session()
        session.headers = {"test_name": "test_response_headers_merged_into_session"}
        expected_headers = session.headers | dict(prepared_request.headers)

        executor = RequestsExecutor(
            req_or_res=response, expected_status_code=200, session=session
        )

        assert executor.session.headers == expected_headers

    def test_self_request_is_first_response_request(
        self, response: Response, prepared_request: PreparedRequest
    ):
        response.request = prepared_request

        executor = RequestsExecutor(req_or_res=response, expected_status_code=200)

        assert executor.request == prepared_request

    def test_self_request_is_first_request_from_history(
        self,
        response: Response,
        headers_response: Response,
        prepared_request: PreparedRequest,
    ):
        additional_response = Response()
        additional_response.request = prepared_request
        response.history = [additional_response, headers_response]

        response.request = PreparedRequest()
        response.request.prepare_headers({})

        executor = RequestsExecutor(req_or_res=response, expected_status_code=200)

        assert executor.request == prepared_request
