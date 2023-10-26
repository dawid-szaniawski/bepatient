"""A library facilitating work with asynchronous APIs."""
import logging
from logging import NullHandler

from .api import (
    RequestsWaiter,
    to_curl,
    wait_for_value_in_request,
    wait_for_values_in_request,
)
from .waiter_src.checker import Checker
from .waiter_src.checkers import CHECKERS
from .waiter_src.comparators import COMPARATORS

__version__ = "0.5.1"
__all__ = [
    "to_curl",
    "wait_for_values_in_request",
    "wait_for_value_in_request",
    "RequestsWaiter",
    "Checker",
    "CHECKERS",
    "COMPARATORS",
]

logging.getLogger(__name__).addHandler(NullHandler())
