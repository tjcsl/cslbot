from typing import Dict, List, Optional, Tuple, Union

from .command import Command
from .hook import Hook

class Registry(object):

    def __init__(self) -> None:
        ...

    def is_disabled(self, obj: str) -> bool:
        ...

    def register(self, obj: Union[Hook, Command], name: Optional[str] = None) -> None:
        ...

    def scan_for_objects(self, obj_type: str) -> List[Tuple[str, str]]:
        ...

    def disable_object(self, obj_type: str, obj: str) -> str:
        ...

    def enable_object(self, obj_type: str, obj: str) -> str:
        ...


class HookRegistry(Registry):

    def scan_for_hooks(self) -> List[Tuple[str, str]]:
        ...

    def get_known_hooks(self) -> Dict[str, Command]:
        ...

    def get_hook_objects(self) -> List[Command]:
        ...

    def get_enabled_hooks(self) -> List[str]:
        ...

    def get_disabled_hooks(self) -> List[str]:
        ...

    def disable_hook(self, hook: str) -> str:
        ...

    def enable_hook(self, hook: str) -> str:
        ...


hook_registry = ...  # type: HookRegistry


class CommandRegistry(Registry):

    def scan_for_commands(self) -> List[Tuple[str, str]]:
        ...

    def get_known_commands(self) -> Dict[str, Command]:
        ...

    def get_enabled_commands(self) -> List[str]:
        ...

    def get_disabled_commands(self) -> List[str]:
        ...

    def is_registered(self, command_name: str) -> bool:
        ...

    def get_command(self, command_name: str) -> Command:
        ...

    def disable_command(self, command: str) -> str:
        ...

    def enable_command(self, command: str) -> str:
        ...


command_registry = ...  # type: CommandRegistry
