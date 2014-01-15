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
import re
from random import choice
from helpers.command import Command


@Command('errno')
def cmd(send, msg, args):
    """Return either a random value or the specified one from errno.h.
    Syntax: !errno <errorcode|list>
    """
    errno = subprocess.check_output(['gcc', '-include', 'errno.h', '-fdirectives-only', '-E', '-xc', '/dev/null'])
    errors = re.findall('^#define (E[A-Z]*) ([0-9]+)', errno.decode(), re.MULTILINE)
    errtoval = dict((x, y) for x, y in errors)
    valtoerr = dict((y, x) for x, y in errors)
    if not msg:
        msg = choice(list(valtoerr.keys()))
    if msg == 'list':
        send(", ".join(errtoval.keys()))
    elif msg in errtoval:
        send('#define %s %s' % (msg, errtoval[msg]))
    elif msg in valtoerr:
        send('#define %s %s' % (valtoerr[msg], msg))
    else:
        send("%s not found in errno.h" % msg)
