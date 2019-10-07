# Stubs for absl.flags._defines (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional


def DEFINE(parser: Any,
           name: Any,
           default: Any,
           help: Any,
           flag_values: Any = ...,
           serializer: Optional[Any] = ...,
           module_name: Optional[Any] = ...,
           **args: Any) -> None:
    ...


def DEFINE_flag(flag: Any, flag_values: Any = ..., module_name: Optional[Any] = ...) -> None:
    ...


def declare_key_flag(flag_name: Any, flag_values: Any = ...) -> None:
    ...


def adopt_module_key_flags(module: Any, flag_values: Any = ...) -> None:
    ...


def disclaim_key_flags() -> None:
    ...


def DEFINE_string(name: Any, default: Any, help: Any, flag_values: Any = ..., **args: Any) -> None:
    ...


def DEFINE_boolean(name: Any, default: Any, help: Any, flag_values: Any = ..., module_name: Optional[Any] = ..., **args: Any) -> None:
    ...


def DEFINE_float(name: Any,
                 default: Any,
                 help: Any,
                 lower_bound: Optional[Any] = ...,
                 upper_bound: Optional[Any] = ...,
                 flag_values: Any = ...,
                 **args: Any) -> None:
    ...


def DEFINE_integer(name: Any,
                   default: Any,
                   help: Any,
                   lower_bound: Optional[Any] = ...,
                   upper_bound: Optional[Any] = ...,
                   flag_values: Any = ...,
                   **args: Any) -> None:
    ...


def DEFINE_enum(name: Any, default: Any, enum_values: Any, help: Any, flag_values: Any = ..., module_name: Optional[Any] = ..., **args: Any) -> None:
    ...


def DEFINE_enum_class(name: Any, default: Any, enum_class: Any, help: Any, flag_values: Any = ..., module_name: Optional[Any] = ...,
                      **args: Any) -> None:
    ...


def DEFINE_list(name: Any, default: Any, help: Any, flag_values: Any = ..., **args: Any) -> None:
    ...


def DEFINE_spaceseplist(name: Any, default: Any, help: Any, comma_compat: bool = ..., flag_values: Any = ..., **args: Any) -> None:
    ...


def DEFINE_multi(parser: Any,
                 serializer: Any,
                 name: Any,
                 default: Any,
                 help: Any,
                 flag_values: Any = ...,
                 module_name: Optional[Any] = ...,
                 **args: Any) -> None:
    ...


def DEFINE_multi_string(name: Any, default: Any, help: Any, flag_values: Any = ..., **args: Any) -> None:
    ...


def DEFINE_multi_integer(name: Any,
                         default: Any,
                         help: Any,
                         lower_bound: Optional[Any] = ...,
                         upper_bound: Optional[Any] = ...,
                         flag_values: Any = ...,
                         **args: Any) -> None:
    ...


def DEFINE_multi_float(name: Any,
                       default: Any,
                       help: Any,
                       lower_bound: Optional[Any] = ...,
                       upper_bound: Optional[Any] = ...,
                       flag_values: Any = ...,
                       **args: Any) -> None:
    ...


def DEFINE_multi_enum(name: Any, default: Any, enum_values: Any, help: Any, flag_values: Any = ..., case_sensitive: bool = ..., **args: Any) -> None:
    ...


def DEFINE_multi_enum_class(name: Any,
                            default: Any,
                            enum_class: Any,
                            help: Any,
                            flag_values: Any = ...,
                            module_name: Optional[Any] = ...,
                            **args: Any) -> None:
    ...


def DEFINE_alias(name: Any, original_name: Any, flag_values: Any = ..., module_name: Optional[Any] = ...):
    ...
