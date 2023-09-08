"""A library facilitating work with asynchronous APIs."""
import logging
from logging import NullHandler

from .api import (
    RequestsWaiter,
    to_curl,
    wait_for_value_in_request,
    wait_for_values_in_request,
)
from .waiter_src.checkers import CHECKERS
from .waiter_src.comparators import COMPARATORS

__version__ = "0.3.0"
__all__ = [
    "to_curl",
    "wait_for_values_in_request",
    "wait_for_value_in_request",
    "RequestsWaiter",
    "CHECKERS",
    "COMPARATORS",
]

logging.getLogger(__name__).addHandler(NullHandler())
