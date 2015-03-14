# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from helpers.misc import list_fortunes, get_fortune
from helpers.command import Command


@Command(['fortune', 'bofh', 'excuse'], ['name'])
def cmd(send, msg, args):
    """Returns a fortune.
    Syntax: !fortune <list|(-a|-o) (module)>
    """
    if msg == 'list':
        fortunes = list_fortunes() + list_fortunes(True)
        send(" ".join(fortunes))
    else:
        output = get_fortune(msg, args['name'])
        for line in output.splitlines():
            send(line)
