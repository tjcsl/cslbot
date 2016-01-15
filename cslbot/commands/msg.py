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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from ..helpers import arguments
from ..helpers.command import Command


@Command('msg', ['nick', 'config'], admin=True)
def cmd(send, msg, args):
    """Sends a message to a channel
    Syntax: {command} <channel> <message>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('channel', action=arguments.ChanParser)
    parser.add_argument('message', nargs='+')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    cmdargs.message = ' '.join(cmdargs.message)
    send(cmdargs.message, target=cmdargs.channels[0])
    send("%s sent message %s to %s" % (args['nick'], cmdargs.message, cmdargs.channels[0]), target=args['config']['core']['ctrlchan'])
