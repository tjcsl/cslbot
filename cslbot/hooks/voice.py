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

from ..helpers.hook import Hook


@Hook("voice", ["pubmsg", "action"], ["nick", "target", "handler", "config"])
def handle(send, _, args):
    if not args["config"].getboolean("feature", "voiceactive"):
        return
    with args["handler"].data_lock:
        if not args["handler"].voiced[args["target"]].get(args["nick"]):
            args["handler"].connection.mode(args["target"], "+v %s" % args["nick"])
