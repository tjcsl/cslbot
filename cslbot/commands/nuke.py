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

from ..helpers.command import Command
from ..helpers.misc import do_nuke


@Command("nuke", ["nick", "handler", "target", "config", "botnick"], role="admin")
def cmd(send, msg, args):
    """Nukes somebody.

    Syntax: {command} <target>

    """
    c, nick = args["handler"].connection, args["nick"]
    channel = args["target"] if args["target"] != "private" else args["config"]["core"]["channel"]
    if not msg:
        send("Nuke who?")
        return
    with args["handler"].data_lock:
        users = args["handler"].channels[channel].users()
    if msg in users:
        do_nuke(c, nick, msg, channel)
    elif msg == args["botnick"]:
        send("Sorry, Self-Nuking is disabled pending aquisition of a Lead-Lined Fridge.")
    else:
        send("I'm sorry. Anonymous Nuking is not allowed")
