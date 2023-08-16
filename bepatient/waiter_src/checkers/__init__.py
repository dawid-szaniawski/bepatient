from typing import Literal

from .response_checkers import HeadersChecker, JsonChecker

CHECKERS = Literal["json_checker", "headers_checker"]

RESPONSE_CHECKERS = {"json_checker": JsonChecker, "headers_checker": HeadersChecker}
