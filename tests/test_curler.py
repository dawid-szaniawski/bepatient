from requests import PreparedRequest, Response

from bepatient.curler import Curler


class TestRequestCurl:
    def test_request_to_curl(self, prepared_request: PreparedRequest):
        curl = (
            "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
            "https://webludus.pl/"
        )
        assert Curler().to_curl(prepared_request) == curl

    def test_request_without_headers_and_body(self):
        curl = "curl -X GET https://webludus.pl/"
        prepared_request = PreparedRequest()
        prepared_request.prepare(method="get", url="https://webludus.pl")

        assert Curler().to_curl(prepared_request) == curl

    def test_with_utm(self, prepared_request: PreparedRequest):
        prepared_request.url += (  # type: ignore
            "?utm_source=pytest&utm_medium=tests&utm_campaign=bepatient"
        )
        curl = (
            "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' https://"
            "webludus.pl/?utm_source=pytest&utm_medium=tests&utm_campaign=bepatient"
        )

        assert Curler().to_curl(prepared_request) == curl

    def test_post_json(self):
        request = PreparedRequest()
        request.prepare(
            method="post",
            url="https://webludus.pl",
            headers={"task": "test"},
            cookies={"user-token": "abc-123"},
            json={"login": "admin", "password": "admin1"},
        )
        expected_curl = (
            "curl -X POST -H 'task: test' -H 'Cookie: user-token=abc-123'"
            " -H 'Content-Length: 40' -H 'Content-Type: application/json' -d "
            '\'{"login": "admin", "password": "admin1"}\' https://webludus.pl/'
        )

        assert Curler().to_curl(request) == expected_curl

    def test_data(self):
        request = PreparedRequest()
        request.prepare(
            method="post",
            url="https://webludus.pl",
            headers={"task": "test"},
            cookies={"user-token": "abc-123"},
            data={"login": "admin", "password": "admin1"},
        )
        expected_curl = (
            "curl -X POST -H 'task: test' -H 'Cookie: user-token=abc-123'"
            " -H 'Content-Length: 27' -H"
            " 'Content-Type: application/x-www-form-urlencoded'"
            " -d 'login=admin&password=admin1' https://webludus.pl/"
        )

        assert Curler().to_curl(request) == expected_curl

    def test_post_with_charset(self):
        request = PreparedRequest()
        request.prepare(
            method="post",
            url="https://webludus.pl",
            headers={"Content-Type": "text/plain"},
            json={"PL": "ąćęłńóśźż"},
        )
        expected_curl = (
            "curl -X POST -H 'Content-Type: text/plain' -H 'Content-Length: 64'"
            ' -d \'{"PL": "ąćęłńóśźż"}\' https://webludus.pl/'
        )
        assert Curler().to_curl(request, charset="unicode-escape") == expected_curl

    def test_response(self, prepared_request: PreparedRequest):
        prepared_request.headers.update({"content-length": "44"})
        response = Response()
        response.request = prepared_request
        curl = (
            "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123'"
            " https://webludus.pl/"
        )

        assert Curler().to_curl(response) == curl

    def test_response_with_utm(self, prepared_request: PreparedRequest):
        prepared_request.url += (  # type: ignore
            "?utm_source=pytest&utm_medium=tests&utm_campaign=bepatient"
        )
        response = Response()
        response.request = prepared_request
        curl = (
            "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' https://"
            "webludus.pl/?utm_source=pytest&utm_medium=tests&utm_campaign=bepatient"
        )

        assert Curler().to_curl(response) == curl
