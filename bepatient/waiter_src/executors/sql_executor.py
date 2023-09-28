import sqlite3

from mysql.connector.cursor import CursorBase as MySqlCursor
from psycopg2.extensions import cursor as Psycopg2Cursor

from bepatient.waiter_src.executor import Executor


class SQLExecutor(Executor):
    """An abstract base class for defining an executor that can be waited for."""

    def __init__(
        self, cursor: sqlite3.Cursor | Psycopg2Cursor | MySqlCursor, query: str
    ):
        """Cursor should have cursor_factory that returns dict object"""
        super().__init__()
        self._cursor = cursor
        self._input: str = query

    def is_condition_met(self) -> bool:
        """Check whether the condition has been met.

        Returns:
            bool: True if the condition has been met, False otherwise."""
        self._result = self._cursor.execute(self._input).fetchall()

        self._failed_checkers = [
            checker for checker in self._checkers if not checker.check(self._result)
        ]

        if len(self._failed_checkers) == 0:
            return True
        return False
