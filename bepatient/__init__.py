"""A library facilitating work with asynchronous APIs"""

import logging
from logging import NullHandler

from .api import (
    RequestsWaiter,
    dict_differences,
    to_curl,
    wait_for_value_in_request,
    wait_for_values_in_request,
)
from .waiter_src.checkers import CHECKERS
from .waiter_src.checkers.checker import Checker
from .waiter_src.comparators import COMPARATORS

__version__ = "0.12.0"
__all__ = [
    "Checker",
    "CHECKERS",
    "COMPARATORS",
    "dict_differences",
    "RequestsWaiter",
    "to_curl",
    "wait_for_values_in_request",
    "wait_for_value_in_request",
]

logging.getLogger(__name__).addHandler(NullHandler())
