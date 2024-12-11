from typing import Any

from bepatient.waiter_src.checkers.checker import Checker


class ConditionsManager:

    def __init__(self):
        self._abort_conditions: list[Checker] = []
        self._preconditions: list[Checker] = []
        self._conditions: list[Checker] = []
        self._failed_checkers: list[Checker] = []

    @staticmethod
    def execute_checkers(
        checkers: list[Checker], result: Any, check_uuid: str
    ) -> list[Checker]:
        return [
            checker for checker in checkers if not checker.check(result, check_uuid)
        ]

    def check_all(self, result: Any, check_uuid: str) -> list[Checker]:
        if self.execute_checkers(self._abort_conditions, result, check_uuid):
            # TODO: Error like AbortConditionMet
            raise AssertionError("Holy Shit")

        self._failed_checkers = self.execute_checkers(
            self._preconditions, result, check_uuid
        )
        if not self._failed_checkers:
            self._failed_checkers = self.execute_checkers(
                self._conditions, result, check_uuid
            )

        return self._failed_checkers
