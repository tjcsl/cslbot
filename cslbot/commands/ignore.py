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

from ..helpers import arguments, misc
from ..helpers.command import Command
from ..helpers.orm import Ignore


@Command("ignore", ["config", "db", "nick"], role="admin")
def cmd(send, msg, args):
    """Handles ignoring/unignoring people
    Syntax: {command} <--clear|--show/--list|--delete|nick>
    """
    parser = arguments.ArgParser(args["config"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--clear", action="store_true")
    group.add_argument("--show", "--list", action="store_true")
    group.add_argument("--delete", "--remove", action="store_true")
    parser.add_argument("nick", nargs="?")
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    session = args["db"]
    if cmdargs.clear:
        session.query(Ignore).delete()
        send("Ignore list cleared.")
    elif cmdargs.show:
        ignored = session.query(Ignore).all()
        if ignored:
            send(", ".join([x.nick for x in ignored]))
        else:
            send("Nobody is ignored.")
    elif cmdargs.delete:
        if not cmdargs.nick:
            send("Unignore who?")
        else:
            row = session.query(Ignore).filter(Ignore.nick == cmdargs.nick).first()
            if row is None:
                send("%s is not ignored." % cmdargs.nick)
            else:
                session.delete(row)
                send("%s is no longer ignored." % cmdargs.nick)
    elif cmdargs.nick:
        send(
            "%s ignored %s" % (args["nick"], cmdargs.nick),
            target=args["config"]["core"]["ctrlchan"],
        )
        send(misc.ignore(session, cmdargs.nick))
    else:
        send("Ignore who?")
