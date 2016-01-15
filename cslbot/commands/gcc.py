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

import subprocess
import tempfile

from ..helpers.command import Command
from ..helpers.textutils import gen_slogan


@Command('gcc', ['type', 'nick'])
def cmd(send, msg, args):
    """Compiles stuff.
    Syntax: {command} <code>
    """
    if args['type'] == 'privmsg':
        send('GCC is a group exercise!')
        return
    tmpfile = tempfile.NamedTemporaryFile()
    for line in msg.split('\\n'):
        line = line + '\n'
        tmpfile.write(line.encode())
    tmpfile.flush()
    process = subprocess.Popen(['gcc', '-o', '/dev/null', '-xc', tmpfile.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    tmpfile.close()
    # Take the last 3 lines to prevent Excess Flood on long error messages
    output = output.decode().splitlines()[:3]
    for line in output:
        send(line, target=args['nick'])
    if process.returncode == 0:
        send(gen_slogan("gcc victory"))
    else:
        send(gen_slogan("gcc failed"))
