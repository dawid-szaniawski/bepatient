import pytest
from requests import Response


@pytest.fixture
def response_without_cookies_in_request(example_response: Response) -> Response:
    del example_response.request.headers["Cookie"]
    return example_response
