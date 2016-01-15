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

from ipaddress import ip_network

from ..helpers.command import Command


@Command('cidr', [])
def cmd(send, msg, args):
    """Gets a CIDR range.
    Syntax: {command} <range>
    """
    if not msg:
        send("Need a CIDR range.")
        return
    try:
        ipn = ip_network(msg)
    except ValueError:
        send("Not a valid CIDR range.")
        return
    send("%s - %s" % (ipn[0], ipn[-1]))
