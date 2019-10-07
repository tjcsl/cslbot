from datetime import datetime
from typing import Any


def or_(*clauses) -> bool:
    ...


def create_engine(*args: Any, **kwargs: Any):
    ...


class Column:

    def __init__(self, *args, **kwargs) -> None:
        ...

    def __ge__(self, other):
        ...

    def __gt__(self, other):
        ...

    def desc(self) -> Any:
        ...

    def __eq__(self, other) -> bool:
        ...

    def __ne__(self, other) -> bool:
        ...


class UnicodeText(Column, str):
    ...


class Unicode(Column, str):
    ...


class DateTime(Column, datetime):
    ...


class Integer(Column, int):
    ...


class Index:

    def __init__(self, name, *expressions, **kwargs) -> None:
        ...
