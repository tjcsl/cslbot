# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from ..helpers.command import Command
from ..helpers.registry import command_registry


@Command('help', ['nick', 'config'])
def cmd(send, msg, args):
    """Gives help.

    Syntax: {command} [command]

    """
    cmdchar = args['config']['core']['cmdchar']
    if msg:
        if msg.startswith(cmdchar):
            msg = msg[len(cmdchar):]
        if len(msg.split()) > 1:
            send("One argument only")
        elif not command_registry.is_registered(msg):
            send("Not a module.")
        else:
            doc = command_registry.get_command(msg).get_doc()
            if doc is None:
                send("No documentation found.")
            else:
                for line in doc.splitlines():
                    send(line.format(command=cmdchar + msg), target=args['nick'])
    else:
        modules = sorted(command_registry.get_enabled_commands())
        cmdlist = (' %s' % cmdchar).join(modules)
        send('Commands: %s%s' % (cmdchar, cmdlist), target=args['nick'], ignore_length=True)
        send('%shelp <command> for more info on a command.' % cmdchar, target=args['nick'])
