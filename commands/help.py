# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from inspect import getdoc

args = ['modules', 'nick', 'connection', 'config']


def cmd(send, msg, args):
    """Gives help.
    Syntax: !help <command>
    """
    cmdchar = args['config']['core']['cmdchar']
    if msg:
        if msg[0] == cmdchar:
            msg = msg[1:]
        if len(msg.split()) > 1:
            send("One argument only")
            return
        if msg not in args['modules']:
            send("Not a module.")
            return
        else:
            doc = getdoc(args['modules'][msg].cmd)
            if doc is None:
                send("No documentation found.")
            else:
                for line in doc.splitlines():
                    send(line)
    else:
        modules = sorted(args['modules'])
        num = int(len(modules) / 2)
        cmdlist1 = (' %s' % cmdchar).join([x for x in modules[:num]])
        cmdlist2 = (' %s' % cmdchar).join([x for x in modules[num:]])
        args['connection'].privmsg(args['nick'], 'Commands: %s%s' % (cmdchar, cmdlist1))
        args['connection'].privmsg(args['nick'], '%s%s' % (cmdchar, cmdlist2))
        args['connection'].privmsg(args['nick'], '%shelp <command> for more info on a command.' % cmdchar)
