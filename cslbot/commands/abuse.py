# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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
from ..helpers.orm import Ignore


@Command("abuse", ["config", "db", "handler"], role="admin")
def cmd(send, msg, args):
    """Shows or clears the abuse list
    Syntax: {command} <--clear|--show>
    """
    parser = arguments.ArgParser(args["config"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--clear", action="store_true")
    group.add_argument("--show", action="store_true")
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.clear:
        args["handler"].abuselist.clear()
        send("Abuse list cleared.")
    elif cmdargs.show:
        abusers = []
        for x in args["handler"].abuselist.keys():
            if args["db"].query(Ignore).filter(Ignore.nick == x).count():
                abusers.append(x)
        if abusers:
            send(", ".join(abusers))
        else:
            send("No abusers.")
    else:
        send("Please specify an option.")
