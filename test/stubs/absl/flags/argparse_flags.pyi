# Stubs for absl.flags.argparse_flags (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import argparse
from typing import Any, Optional


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, **kwargs: Any) -> None:
        ...

    def parse_known_args(self, args: Optional[Any] = ..., namespace: Optional[Any] = ...):
        ...


class _FlagAction(argparse.Action):

    def __init__(self, option_strings: Any, dest: Any, help: Any, metavar: Any, flag_instance: Any) -> None:
        ...

    def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Optional[Any] = ...) -> None:
        ...


class _BooleanFlagAction(argparse.Action):

    def __init__(self, option_strings: Any, dest: Any, help: Any, metavar: Any, flag_instance: Any) -> None:
        ...

    def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Optional[Any] = ...) -> None:
        ...


class _HelpFullAction(argparse.Action):

    def __init__(self, option_strings: Any, dest: Any, default: Any, help: Any) -> None:
        ...

    def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Optional[Any] = ...) -> None:
        ...
