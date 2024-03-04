# Usage

## Quickstart

Getting started with bepatient is quick and easy. The library comes equipped with a
range of default checkers, comparers, and a convenient Waiter object for your use.

In most cases, using one of the two methods will suffice:

```yaml
wait_for_value_in_request: in case of checking 1 condition
wait_for_values_in_request: in case of multiple conditions
```

We can also use the `RequestsWaiter` object. However, it's important to remember that
the default methods only allow the use of built-in checkers and comparers.

However, there is nothing preventing you from adding a new Waiter object that would
introduce its own checkers and comparers.

---

### Basic methods

#### `wait_for_value_in_request`

Waits for a specified value in response.

##### Args:

- request `(PreparedRequest | Request | Response)`: the request or response to monitor
  for the expected value.
- status_code `(int, optional)`: the expected HTTP status code. Defaults to `200`.
- comparer `(COMPARATORS | None, optional)`: the comparer function or operator used for
  value comparison. Defaults to `None`.
- expected_value `(Any, optional)`: the value to be compared against the response data.
  Defaults to `None`.
- checker `(CHECKERS, optional)`: the type of checker to use.
- session `(Session | None, optional)`: the requests session to use for sending
  requests. Defaults to `None`.
- dict_path `(str | None, optional)`: the dot-separated path to the value in the
  response data. Defaults to `None`.
- search_query `(str | None, optional)`: a search query to use to find the value in the
  response data. Defaults to `None`.
- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.
- req_timeout `(int | tuple[int, int] | None, optional)`: request timeout in seconds.
  Default value is `15` for `connect` and `30` for `read`. If user provide one value,
  it will be applied to both - `connect` and `read` timeouts.

##### Returns:

- `Response`: the final response containing the expected value.

##### Raises:

- `WaiterConditionWasNotMet`: if the condition is not met within the specified number
  of attempts.

##### Example:

```python
from requests import get

from bepatient import wait_for_value_in_request

response = wait_for_value_in_request(
    request=get("https://example.com/api"),
    comparer="contain",
    expected_value="string"
)
assert response.status_code == 200
```

---

#### `wait_for_values_in_request`

Wait for multiple specified values in a response using different checkers.

##### Args:

- request `(PreparedRequest | Request | Response)`: the request or response to monitor
  for the expected values.
- checkers `(list[dict[str, Any]])`: list of dictionaries, where each dictionary
  contains information about a checker to apply.
  Each dictionary must have keys:
    * checker `(CHECKERS)`: type of checker to use.
    * comparer `(COMPARATORS)`: comparer function or operator used for value comparison.
    * expected_value `(Any)`: the value to be compared against the response data.
    * dict_path `(str | None, optional)`: the dot-separated path to the value in the
      response data. Defaults to `None`.
    * search_query `(str | None, optional)`: a search query to use to find the value in
      the response data. Defaults to `None`.
    * ignore_case `(bool, optional)`: If set, upper/lower-case keys in `dict_path` are
      treated the same. Defaults to `False`.
- status_code `(int, optional)`: the expected HTTP status code. Defaults to `200`.
- session `(Session | None, optional)`: the requests session to use for sending
  requests. Defaults to `None`.
- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.
- req_timeout `(int | tuple[int, int] | None, optional)`: request timeout in seconds.
  Default value is 15 for `connect` and 30 for `read`. If user provide one value, it
  will be applied to both - `connect` and `read` timeouts.

##### Returns:

- `Response`: the final response containing the expected value.

##### Raises:

- `WaiterConditionWasNotMet`: if the condition is not met within the specified number
  of attempts.

##### Example:

```python
from requests import get

from bepatient import wait_for_value_in_request

response = wait_for_value_in_request(
    request=get("https://example.com/api"),
    comparer="contain",
    expected_value="string"
)
assert response.status_code == 200
```

Both of the above methods use the `RequestsWaiter` object.

---

### RequestsWaiter

The `RequestsWaiter` class is a utility class designed to facilitate the setup and
monitoring of requests to ensure expected values are met.

#### Args

When creating a RequestsWaiter object, one attribute is required:

- request `(PreparedRequest | Request | Response)`: the request or response to monitor
  for the expected values.

Additionally, the user can also specify:

- status_code `(int, optional)`: the expected HTTP status code. Defaults to `200`.
- session `(Session | None, optional)`: the requests session to use for sending
  requests. Defaults to `None`.
- timeout `(int | tuple[int, int] | None, optional)`: request timeout in seconds.
  Default value is `15` for `connect` and `30` for `read`. If user provide one
  value, it will be applied to both - `connect` and `read` timeouts.

#### Methods

##### add_checker

Add a response checker to the waiter.

###### Args:

- expected_value `(Any)`: the value to be compared against the response data.
- comparer `(COMPARATORS)`: the comparer function or operator used for value comparison.
- checker `(CHECKERS, optional)`: the type of checker to use. Defaults
  to `json_checker`.
- dict_path `(str | None, optional)`: the dot-separated path to the value in the
  response data. Defaults to `None`.
- search_query `(str | None, optional)`: a search query to use to find the value in the
  response data. Defaults to `None`.
- ignore_case `(bool, optional)`: If set, upper/lower-case keys in `dict_path` are
  treated the same. Defaults to `False`.

###### Returns:

- `self`: updated `RequestsWaiter` instance.

##### add_custom_checker

This method allows users to add their own custom response checker by providing an
object that inherits from the abstract base class `Checker`.

###### Args:

- checker `(Checker)`: an instance of a custom checker object that inherits from the
  `Checker` class.

###### Returns:

- `self`: updated `RequestsWaiter` instance.

##### run

Run the waiter and monitor the specified request or response.

###### Args:

- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.
- raise_error `(bool, optional)`: raises WaiterConditionWasNotMet. Defaults to `True`.

###### Returns:

- `self`: updated `RequestsWaiter` instance.

###### Raises:

- `WaiterConditionWasNotMet`: if the condition is not met within the specified number
  of attempts.

##### get_result

Get the final response containing the expected values.

###### Returns:

- `Response`: final response containing the expected values.

#### Example

```python
from requests import Request, Session

from bepatient import RequestsWaiter

# Create a Request instance (you can also use Response and PreparedRequest objects)
req = Request(method="get", url="https://example.com/api/endpoint")

# Create a Session instance (optional)
patient_session = Session()
patient_session.headers["Authorization"] = "Bearer JWT"
patient_session.headers["User-Agent"] = "bepatient"

# Create a RequestsWaiter instance with a request and expected status code
waiter = RequestsWaiter(request=req, status_code=200, session=patient_session)

# Add a checker to monitor for an expected value
waiter.add_checker(
    expected_value=0,
    comparer="have_len_greater",
    checker="json_checker",
    dict_path="data"
)

# Run the waiter and monitor the response
response = waiter.run(retries=5, delay=2).get_result()

# Access the final response containing the expected values
print(response)
```

---
