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

import os
import subprocess
from random import choice

from ..helpers.command import Command


@Command("eix", limit=10)
def cmd(send, msg, args):
    """Runs eix with the given arguments.

    Syntax: {command} <package>

    """
    if not msg:
        result = subprocess.run(
            ["eix", "-c"],
            env={"EIX_LIMIT": "0", "HOME": os.environ["HOME"]},
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        if result.returncode:
            send("eix what?")
            return
        send(choice(result.stdout.splitlines()))
        return
    args = ["eix", "-c"] + msg.split()
    result = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
    )
    if result.returncode:
        send("%s isn't important enough for Gentoo." % msg)
    else:
        send(result.stdout.splitlines()[0].strip())
