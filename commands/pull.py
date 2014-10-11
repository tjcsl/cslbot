# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import subprocess
from helpers.command import Command
from helpers.misc import do_pull


@Command('pull', ['handler', 'is_admin', 'nick', 'botnick'])
def cmd(send, msg, args):
    """Pull changes.
    Syntax: !pull <branch>
    """
    if not args['is_admin'](args['nick']):
        send("Nope, not gonna do it.")
    else:
        try:
            send(do_pull(args['handler'].srcdir, args['botnick']))
        except subprocess.CalledProcessError as e:
            for line in e.output.decode().splitlines():
                send(line)
