# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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


@Command('wtf')
def cmd(send, msg, args):
    """Tells you what things mean.
    Syntax: !wtf <term>
    """
    try:
        answer = subprocess.check_output(['wtf', msg], stderr=subprocess.STDOUT)
        send(answer.decode().rstrip().replace('\n', ' or ').replace('fuck',
            'fsck').replace('\r', ' '))
    except subprocess.CalledProcessError as ex:
        send(ex.output.decode().rstrip())
