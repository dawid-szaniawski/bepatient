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

### Basic methods

#### `wait_for_value_in_request`

Waits for a specified value in response.


##### Args:  
- request `(PreparedRequest | Response)`: The request or response to monitor for the
expected value.
- status_code `(int, optional)`: The expected HTTP status code. Defaults to 200.
- comparer `(COMPARATORS | None, optional)`: The comparer function or operator used for
value comparison. Defaults to None.
- expected_value `(Any, optional)`: The value to be compared against the response data.
Defaults to None.
- checker `(CHECKERS, optional)`: The type of checker to use.
- session `(Session | None, optional)`: The requests session to use for sending
requests. Defaults to None.
- dict_path `(str | None, optional)`: The dot-separated path to the value in the
response data. Defaults to None.
- search_query `(str | None, optional)`: A search query to use to find the value in the
response data. Defaults to None.
- retries `(int, optional)`: The number of retries to perform. Defaults to 60.
- delay `(int, optional)`: The delay between retries in seconds. Defaults to 1.

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

#### `wait_for_values_in_request`

Wait for multiple specified values in a response using different checkers.

##### Args:  
- request `(PreparedRequest | Response)`: The request or response to monitor for the
expected values.
- checkers `(list[dict[str, Any]])`: A list of dictionaries, where each dictionary
contains information about a checker to apply. 
  Each dictionary must have keys:
    * checker `(CHECKERS)`: type of checker to use.
    * comparer `(COMPARATORS)`: comparer function or operator used for value comparison.
    * expected_value `(Any)`: the value to be compared against the response data.
    * dict_path `(str | None, optional)`: The dot-separated path to the value in the
  response data. Defaults to None.
    * search_query `(str | None, optional)`: A search query to use to find the value in
  the response data. Defaults to None.
- status_code `(int, optional)`: The expected HTTP status code. Defaults to 200.
- session `(Session | None, optional)`: The requests session to use for sending
requests. Defaults to None.
- retries `(int, optional)`: The number of retries to perform. Defaults to 60.
- delay `(int, optional)`: The delay between retries in seconds. Defaults to 1.

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

### RequestsWaiter

The `RequestsWaiter` class is a utility class designed to facilitate the setup and
monitoring of requests to ensure expected values are met.

#### Args

When creating a RequestsWaiter object, one attribute is required:

- request `(PreparedRequest | Response)`: The request or response to monitor for the
expected values.

Additionally, the user can also specify:

- status_code `(int, optional)`: The expected HTTP status code. Defaults to 200.
- session `(Session | None, optional)`: The requests session to use for sending
requests. Defaults to None.

#### Methods

##### add_checker

Add a response checker to the waiter.

###### Args:
- expected_value `(Any)`: The value to be compared against the response data.
- comparer `(COMPARATORS)`: The comparer function or operator used for  value comparison.
- checker `(CHECKERS, optional)`: The type of checker to use. Defaults to "json_checker".
- dict_path `(str | None, optional)`: The dot-separated path to the value in the
response data. Defaults to None.
- search_query `(str | None, optional)`: A search query to use to find the value in the
response data. Defaults to None.

###### Returns:

- `self`: updated `RequestsWaiter` instance.

##### run

Run the waiter and monitor the specified request or response.

###### Args:
- retries `(int, optional)`: The number of retries to perform. Defaults to `60`.
- delay `(int, optional)`: The delay between retries in seconds. Defaults to `1`.

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
from requests import get

from bepatient import RequestsWaiter

# Create a RequestsWaiter instance with a request and expected status code
waiter = RequestsWaiter(request=get("https://example.com/api"), status_code=200)

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

### Default checkers

When working with bepatient, you'll find that each checking object should inherit from
the `Checker` class or one of its derived classes.
At the moment, _bepatient_ exclusively supports response checkers:

```yaml
checkers:
  - json_checker
  - headers_checker
```

Furthermore, it's important to note that `RequestsExecutor` requires the `status_code`
attribute. This is because, prior to evaluating other checkers, it employs the
`StatusCodeChecker`, a subclass of `ResponseChecker`.

For an extensive list of available checkers, refer to:

```python
from bepatient import CHECKERS


print(CHECKERS)
```

### Default comparers

Comparers serve as straightforward functions designed to compare two objects and return
a boolean value. _bepatient_ offers a comprehensive range of default comparers,
all designed to suit your testing needs. They can be accessed here:

```python
from bepatient import COMPARATORS


print(COMPARATORS)
```

The basic comparers include:
```yaml
comparators:
  - is_equal
  - is_not_equal
  - is_greater_than
  - is_lesser_than
  - is_greater_than_or_equal
  - is_lesser_than_or_equal
  - not_contain
  - contain_all
  - contain_any
  - have_len_equal
  - have_len_greater
  - have_len_lesser
```
