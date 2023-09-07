import pytest
from requests import PreparedRequest, Session, Response

from bepatient import (
    RequestsWaiter,
    wait_for_value_in_request,
    wait_for_values_in_request,
    to_curl,
)
from bepatient.waiter_src.checkers.response_checkers import HeadersChecker
from bepatient.waiter_src.comparators import is_equal
from bepatient.waiter_src.exceptions.waiter_exceptions import WaiterConditionWasNotMet


def test_to_curl(prepared_request: PreparedRequest):
    expected_curl = (
        "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
        "https://webludus.pl/"
    )

    assert to_curl(prepared_request) == expected_curl


class TestRequestsWaiter:
    def test_init(self, prepared_request: PreparedRequest, session_mock: Session):
        executor = RequestsWaiter(
            request=prepared_request, status_code=201, session=session_mock
        ).executor

        assert executor.request == prepared_request
        assert executor.session == session_mock

        checker = executor._status_code_checker  # pylint: disable=protected-access
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
        w_checker = executor._checkers[0].__dict__  # pylint: disable=protected-access

        checker = HeadersChecker(
            comparer=is_equal,
            expected_value="TEST",
            dict_path="dict",
            search_query="search",
        ).__dict__

        assert w_checker == checker

    def test_happy_path(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        dict_content_response: Response,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=True, comparer="is_equal", dict_path="ok")
        response = waiter.run(retries=1).get_result()

        assert response == dict_content_response

    def test_condition_not_met_raise_error(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        dict_content_response: Response,
        error_msg: str,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=False, comparer="is_equal", dict_path="ok")
        with pytest.raises(WaiterConditionWasNotMet, match=error_msg):
            waiter.run(retries=1)

        assert waiter.get_result() == dict_content_response

    def test_condition_not_met_without_error(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        dict_content_response: Response,
    ):
        waiter = RequestsWaiter(request=prepared_request, session=session_mock)
        waiter.add_checker(expected_value=False, comparer="is_equal", dict_path="ok")
        waiter.run(retries=1, raise_error=False)

        assert waiter.get_result() == dict_content_response


class TestWaitForValueInRequests:
    def test_happy_path(
        self,
        prepared_request: PreparedRequest,
        session_mock: Session,
        dict_content_response: Response,
    ):
        result = wait_for_value_in_request(
            request=prepared_request,
            session=session_mock,
            comparer="is_equal",
            expected_value=True,
            dict_path="ok",
            retries=1,
        )

        assert result == dict_content_response

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
        dict_content_response: Response,
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
                "expected_value": "json",
                "dict_path": "content",
            },
        ]

        response = wait_for_values_in_request(
            request=prepared_request,
            session=session_mock,
            checkers=list_of_checkers,
            retries=1,
        )

        assert response == dict_content_response

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
