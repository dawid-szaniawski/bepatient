import pytest
from requests import get

from bepatient import (
    RequestsWaiter,
    wait_for_value_in_request,
    wait_for_values_in_request,
)


@pytest.mark.e2e
class TestRequestsWaiter:
    def test_pokeapi(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )

        waiter = RequestsWaiter(
            request=get("https://pokeapi.co/api/v2/ability/battle-armor", timeout=5)
        )
        waiter.add_checker(
            comparer="contain_all",
            expected_value=(msg,),
            dict_path="effect_entries",
            search_query="effect",
        )
        waiter.run()

        response = waiter.get_result()

        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"

    def test_pokeapi_multiple_checkers(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )
        response = (
            RequestsWaiter(
                request=get(
                    "https://pokeapi.co/api/v2/ability/battle-armor", timeout=5
                ),
            )
            .add_checker(
                expected_value=(msg,),
                comparer="contain_all",
                dict_path="effect_entries",
                search_query="effect",
            )
            .add_checker(
                checker="headers_checker",
                expected_value="cloudflare",
                comparer="is_equal",
                dict_path="Server",
            )
            .run()
            .get_result()
        )

        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"


@pytest.mark.e2e
class TestWaitForValueInRequest:
    def test_pokeapi(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )
        response = wait_for_value_in_request(
            request=get("https://pokeapi.co/api/v2/ability/battle-armor", timeout=5),
            comparer="contain_all",
            expected_value=(msg,),
            checker="json_checker",
            dict_path="effect_entries",
            search_query="effect",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"


@pytest.mark.e2e
class TestWaitForValuesInRequest:
    def test_pokeapi(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )
        list_of_checkers = [
            {
                "checker": "json_checker",
                "comparer": "contain_all",
                "expected_value": (msg,),
                "dict_path": "effect_entries",
                "search_query": "effect",
            },
            {
                "checker": "headers_checker",
                "comparer": "is_equal",
                "expected_value": "cloudflare",
                "dict_path": "Server",
            },
        ]
        response = wait_for_values_in_request(
            request=get("https://pokeapi.co/api/v2/ability/battle-armor", timeout=5),
            checkers=list_of_checkers,  # type: ignore
            retries=5,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"
