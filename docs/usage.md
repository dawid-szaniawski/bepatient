# Usage

## Quickstart

Getting started with bepatient is quick and easy. The library comes equipped with
a range of default checkers, comparers, and a convenient Waiter object for your use.

In most cases, using one of the two methods will suffice:

```yaml
wait_for_value_in_request: in case of checking 1 condition

wait_for_values_in_request: in case of multiple conditions
```

Both of those methods use the `RequestsWaiter` under the hood, so if we want to, we can
simply use `RequestWaiter` adapted to our needs.

However, there is nothing preventing you from adding a new Waiter object that would
introduce its own checkers and comparers.

---

### `wait_for_value_in_request`

Waits for a specified value in response.

#### Args

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

#### Returns

- `Response`: the final response containing the expected value.

#### Example

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

### `wait_for_values_in_request`

Wait for multiple specified values in a response using different checkers.

#### Args

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
    * condition_level `("exception" | "pre" | "main", optional)`: specifies, on what
      stage of validation, that condition should be checked. Defaults to `main`
- status_code `(int, optional)`: the expected HTTP status code. Defaults to `200`.
- session `(Session | None, optional)`: the requests session to use for sending
  requests. Defaults to `None`.
- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.
- req_timeout `(int | tuple[int, int] | None, optional)`: request timeout in seconds.
  Default value is 15 for `connect` and 30 for `read`. If user provide one value, it
  will be applied to both - `connect` and `read` timeouts.

#### Returns

- `Response`: the final response containing the expected value.

#### Example

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

##### Condition levels

- `exception_conditions` - conditions that trigger an exception if not met
(**on the first attempt**).
- `precondition_conditions` - conditions that are checked prior to the main conditions.
- `main_conditions` - core conditions, those are checked last.

Let's take one-time password tests as an example. In that case, we want to send our
request containing OTP and check for a response status code. After that, we want to
check if we have the `__token__` key in response. But what if our password expires
between the time we generate it and the time the application receives it from us?

In that scenario, we can wait for the next password. But if we don't want to do so, we
can use `exception_conditions` and check for the `error` key in response.

#### Methods

##### add_checker

Add a response checker to the waiter.

###### Args

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
- condition_level `("exception" | "pre" | "main", optional)`: specifies, on what stage
  of validation, that condition should be checked. Defaults to `main`

###### Returns

- `self`: updated `RequestsWaiter` instance.

##### add_custom_checker

This method allows users to add their own custom response checker by providing an
object that inherits from the abstract base class `Checker`.

Actually, the `add_checker` method just uses this method underneath, with the
difference that it uses the built-in Checkers.

###### Args

- checker `(Checker)`: an instance of a custom checker object that inherits from the
  `Checker` class.

###### Returns

- `self`: updated `RequestsWaiter` instance.

##### run

Run the waiter and monitor the specified request or response.

###### Args

- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.
- raise_error `(bool, optional)`: raises WaiterConditionWasNotMet. Defaults to `True`.

###### Returns

- `self`: updated `RequestsWaiter` instance.

###### Raises

- `ExecutorIsNotReady` - we raise it when user want to use `get_result` or
  `error_message` methods from the `Executor` before checking if the condition has
  been met.
- `WaiterIsNotReady`: not all required attributes have been set.
- `WaiterConditionWasNotMet`: the conditions were not met within the specified number
  of attempts.
- `ExceptionConditionNotMet`: one of the conditions causing the wait for the result to
  end has not been met.

##### get_result

Get the final response containing the expected values.

###### Returns

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
# <Response [200]>

```

---

### retry

Simple decorator, that retries function if its result is different from expected.

#### Args

- expected `(Any)`: the value to be compared against the returned data.
- comparer `(COMPARATORS)`: the comparer function or operator used for value comparison.
- retries `(int, optional)`: the number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: the delay between retries in seconds. Defaults to `1`.

#### Example

```python
import bepatient
import requests


@bepatient.retry(200)
def send_request() -> int:
    return requests.get('https://example.com').status_code


result = send_request()
assert result == 200
```

---

### to_curl

Converts a `PreparedRequest` or a `Response` object to a `curl` command.

#### Args
- req_or_res `(PreparedRequest | Response)`: The `PreparedRequest` or `Response` 
  object to be converted.
- charset `(str, optional)`: The character set to use for encoding the request body,
  if it is a byte string. Defaults to "utf-8".

#### Returns

The `curl` command as a string

---
