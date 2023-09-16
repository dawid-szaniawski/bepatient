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
allows for the repeated execution of specific actions until the desired effect is achieved.

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

---
