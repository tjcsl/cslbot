# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

from typing import Any, Callable, Dict, List, Set, Union  # noqa

from . import modutils


class Registry(object):

    def __init__(self) -> None:
        self.known_objects = {}  # type: Dict[str,Any]
        self.disabled_objects = set()  # type: Set[Any]

    def is_disabled(self, obj: str) -> bool:
        return obj in self.disabled_objects

    def register(self, obj: Any, name: str = None) -> None:
        if name is None:
            name = obj.name
        if name in self.known_objects:
            raise ValueError("There is already a object registered with the name %s" % obj)
        self.known_objects[name] = obj

    def scan_for_objects(self, obj_type: str) -> List[str]:
        self.known_objects.clear()
        self.disabled_objects = modutils.get_disabled(obj_type)
        errors = modutils.scan_and_reimport(obj_type)
        return errors

    def disable_object(self, obj_type: str, obj: str) -> str:
        if obj not in self.known_objects:
            return "%s is not a loaded %s" % (obj, obj_type)
        if obj not in self.disabled_objects:
            self.disabled_objects.add(obj)
            return "Disabled %s %s" % (obj_type, obj)
        else:
            return "That %s is already disabled!" % obj_type

    def enable_object(self, obj_type: str, obj: str) -> str:
        if obj == "all":
            self.disabled_objects.clear()
            return "Enabled all %ss." % obj_type
        elif obj in self.disabled_objects:
            self.disabled_objects.remove(obj)
            return "Enabled %s %s" % (obj_type, obj)
        elif obj in self.known_objects:
            return "That %s isn't disabled!" % obj_type
        else:
            return "%s is not a loaded %s" % (obj, obj_type)


class HookRegistry(Registry):

    def scan_for_hooks(self) -> List[str]:
        """
        Scans for hooks

        :rtype: list
        :return: A list of modules that failed to reload
        """
        return self.scan_for_objects("hooks")

    # FIXME: generalize these
    def get_known_hooks(self) -> Dict[str, Any]:
        return self.known_objects

    def get_hook_objects(self) -> List[Any]:
        return [self.known_objects[x] for x in self.known_objects if x not in self.disabled_objects]

    def get_enabled_hooks(self) -> List[str]:
        return [x for x in self.known_objects if x not in self.disabled_objects]

    def get_disabled_hooks(self) -> List[str]:
        return [x for x in self.known_objects if x in self.disabled_objects]

    def disable_hook(self, hook: str) -> str:
        """Adds a hook to the disabled hooks list."""
        return self.disable_object("hook", hook)

    def enable_hook(self, hook: str) -> str:
        """Removes a command from the disabled hooks list."""
        return self.enable_object("hook", hook)

hook_registry = HookRegistry()


class CommandRegistry(Registry):

    def scan_for_commands(self) -> List[str]:
        """
        Scans for commands

        :rtype: list
        :return: A list of modules that failed to reload
        """
        return self.scan_for_objects("commands")

    def get_known_commands(self) -> Dict[str, Any]:
        return self.known_objects

    def get_enabled_commands(self) -> List[str]:
        return [x for x in self.known_objects if x not in self.disabled_objects]

    def get_disabled_commands(self) ->List[str]:
        return [x for x in self.known_objects if x in self.disabled_objects]

    def is_registered(self, command_name: str) -> bool:
        return command_name in self.known_objects

    def get_command(self, command_name: str) -> Any:
        return self.known_objects[command_name]

    def disable_command(self, command: str) -> str:
        """Adds a command to the disabled commands list."""
        self.disable_object("command", command)

    def enable_command(self, command: str) -> str:
        """Removes a command from the disabled commands list."""
        return self.enable_object("command", command)

command_registry = CommandRegistry()
