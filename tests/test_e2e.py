from requests import PreparedRequest, get

from bepatient import (
    RequestsWaiter,
    to_curl,
    wait_for_value_in_request,
    wait_for_values_in_request,
)


class TestToCurl:
    def test_happy_path(self, prepared_request: PreparedRequest):
        expected_curl = (
            "curl -X GET -H 'task: test' -H 'Cookie: user-token=abc-123' "
            "https://webludus.pl/"
        )

        assert to_curl(prepared_request) == expected_curl


class TestWaitForValueInRequest:
    def test_pokeapi(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )
        response = wait_for_value_in_request(
            request=get("https://pokeapi.co/api/v2/ability/battle-armor"),
            comparer="contain_all",
            expected_value=(msg,),
            checker="json_checker",
            dict_path="effect_entries",
            search_query="effect",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"


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
            request=get("https://pokeapi.co/api/v2/ability/battle-armor"),
            checkers=list_of_checkers,  # type: ignore
            retries=5,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "battle-armor"


class TestRequestsWaiter:
    def test_pokeapi_2(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )

        waiter = RequestsWaiter(
            request=get("https://pokeapi.co/api/v2/ability/battle-armor")
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

    def test_pokeapi(self):
        msg = (
            "Moves cannot score critical hits against this Pokémon.\n\n"
            "This ability functions identically to shell armor."
        )
        response = (
            RequestsWaiter(
                request=get("https://pokeapi.co/api/v2/ability/battle-armor"),
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
