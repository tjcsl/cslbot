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
import tempfile
from helpers.textutils import gen_slogan
from helpers.command import Command


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
    for line in output.decode().splitlines():
        send(line, target=args['nick'])
    if process.returncode == 0:
        send(gen_slogan("gcc victory"))
    else:
        send(gen_slogan("gcc failed"))
