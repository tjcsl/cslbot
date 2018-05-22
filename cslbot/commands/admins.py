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
from ..helpers.orm import Permissions


@Command("admins", ["db", "nick"])
def cmd(send, _, args):
    """Returns a list of admins.

    V = Verified (authed to NickServ), U = Unverified.
    Syntax: {command}

    """
    adminlist = []
    for admin in args["db"].query(Permissions).order_by(Permissions.nick).all():
        if admin.registered:
            adminlist.append("%s (V)" % admin.nick)
        else:
            adminlist.append("%s (U)" % admin.nick)
    send(", ".join(adminlist), target=args["nick"])
