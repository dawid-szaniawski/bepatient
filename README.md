[![Tests](https://github.com/dawid-szaniawski/bepatient/actions/workflows/tox.yml/badge.svg)](https://github.com/dawid-szaniawski/bepatient/actions/workflows/tox.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bepatient)](https://pypi.org/project/bepatient/)
[![PyPI](https://img.shields.io/pypi/v/bepatient)](https://pypi.org/project/bepatient/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/dawid-szaniawski/bepatient/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/github/dawid-szaniawski/bepatient/branch/master/graph/badge.svg?token=hY7Nb5jGgi)](https://codecov.io/github/dawid-szaniawski/bepatient)
[![CodeFactor](https://www.codefactor.io/repository/github/dawid-szaniawski/bepatient/badge)](https://www.codefactor.io/repository/github/dawid-szaniawski/bepatient)

# Be Patient

_bepatient_ is a library aimed at facilitating work with asynchronous applications. It
allows for the repeated execution of specific actions until the desired effect is
achieved.

## Features

- Set up and monitor requests for expected values.
- Flexible comparison using various checkers and comparers.
- Configure multiple conditions to be met by response.
- Inspect various aspects of the response (body, status code, headers).
- Detailed logs, facilitating the analysis of the test process.
- Retry mechanism with customizable retries and delay.

## Installation

To install _bepatient_, you can use pip:

```bash
pip install bepatient
```

_bepatient_ supports Python 3.10+

## Basic Usage

Using RequestsWaiter object:

```python
from requests import get

from bepatient import RequestsWaiter

waiter = RequestsWaiter(request=get("https://example.com/api"))
waiter.add_checker(comparer="contain", expected_value="string")
waiter.run()

response = waiter.get_result()

assert response.status_code == 200
```

Simple way:

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

If we need add more than one checker:

```python
from requests import get

from bepatient import wait_for_values_in_request

list_of_checkers = [
    {
        "checker": "json_checker",
        "comparer": "contain",
        "expected_value": "string"
    },
    {
        "checker": "headers_checker",
        "comparer": "is_equal",
        "expected_value": "cloudflare",
        "dict_path": "Server",
    },
]
response = wait_for_values_in_request(
    request=get("https://example.com/api"),
    checkers=list_of_checkers,
    retries=5,
)
assert response.status_code == 200
```

## License

MIT License

Copyright (c) 2023-2024 Dawid Szaniawski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
