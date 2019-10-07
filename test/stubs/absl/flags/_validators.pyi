# Stubs for absl.flags._validators (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any


class Validator:
    validators_count: int = ...
    checker: Any = ...
    message: Any = ...
    insertion_index: Any = ...

    def __init__(self, checker: Any, message: Any) -> None:
        ...

    def verify(self, flag_values: Any) -> None:
        ...

    def get_flags_names(self) -> None:
        ...

    def print_flags_with_values(self, flag_values: Any) -> None:
        ...


class SingleFlagValidator(Validator):
    flag_name: Any = ...

    def __init__(self, flag_name: Any, checker: Any, message: Any) -> None:
        ...

    def get_flags_names(self):
        ...

    def print_flags_with_values(self, flag_values: Any):
        ...


class MultiFlagsValidator(Validator):
    flag_names: Any = ...

    def __init__(self, flag_names: Any, checker: Any, message: Any) -> None:
        ...

    def print_flags_with_values(self, flag_values: Any):
        ...

    def get_flags_names(self):
        ...


def register_validator(flag_name: Any, checker: Any, message: str = ..., flag_values: Any = ...) -> None:
    ...


def validator(flag_name: Any, message: str = ..., flag_values: Any = ...):
    ...


def register_multi_flags_validator(flag_names: Any, multi_flags_checker: Any, message: str = ..., flag_values: Any = ...) -> None:
    ...


def multi_flags_validator(flag_names: Any, message: str = ..., flag_values: Any = ...):
    ...


def mark_flag_as_required(flag_name: Any, flag_values: Any = ...):
    ...


def mark_flags_as_required(flag_names: Any, flag_values: Any = ...) -> None:
    ...


def mark_flags_as_mutual_exclusive(flag_names: Any, required: bool = ..., flag_values: Any = ...):
    ...


def mark_bool_flags_as_mutual_exclusive(flag_names: Any, required: bool = ..., flag_values: Any = ...):
    ...
