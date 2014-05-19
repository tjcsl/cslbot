# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from helpers.command import Command, get_commands, get_command, is_registered


@Command('help', ['nick', 'config'])
def cmd(send, msg, args):
    """Gives help.
    Syntax: !help <command>
    """
    cmdchar = args['config']['core']['cmdchar']
    if msg:
        if msg.startswith(cmdchar):
            msg = msg[len(cmdchar):]
        if len(msg.split()) > 1:
            send("One argument only")
        elif not is_registered(msg):
            send("Not a module.")
        else:
            doc = get_command(msg).get_doc()
            if doc is None:
                send("No documentation found.")
            else:
                for line in doc.splitlines():
                    send(line.format(command = cmdchar + msg))
    else:
        modules = sorted(get_commands())
        num = int(len(modules) / 2)
        cmdlist1 = (' %s' % cmdchar).join([x for x in modules[:num]])
        cmdlist2 = (' %s' % cmdchar).join([x for x in modules[num:]])
        send('Commands: %s%s' % (cmdchar, cmdlist1), target=args['nick'])
        send('%s%s' % (cmdchar, cmdlist2), target=args['nick'])
        send('%shelp <command> for more info on a command.' % cmdchar, target=args['nick'])
