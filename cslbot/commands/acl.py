# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
from ..helpers.orm import Permissions


@Command('acl', ['config', 'db'], role="owner")
def cmd(send, msg, args):
    """Handles permissions
    Syntax: {command} (--add|--remove) --nick (nick) --role (admin)
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--nick', action=arguments.NickParser, required=True)
    parser.add_argument('--role', choices=['admin'], required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', action='store_true')
    group.add_argument('--remove', action='store_true')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    session = args['db']
    admin = session.query(Permissions).filter(Permissions.nick == cmdargs.nick).first()
    if cmdargs.add:
        if admin is None:
            session.add(Permissions(nick=cmdargs.nick, role=cmdargs.role))
            send("%s is now an %s." % (cmdargs.nick, cmdargs.role))
        else:
            send("%s is already an %s." % (admin.nick, admin.role))
    else:
        if admin is None:
            send("%s was not an %s." % (cmdargs.nick, cmdargs.role))
        else:
            session.delete(admin)
            send("%s is no longer an %s." % (admin.nick, admin.role))
