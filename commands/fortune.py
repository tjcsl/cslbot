# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

from os.path import basename
import subprocess
import re


def get_list():
    output = subprocess.check_output(['fortune', '-f'], stderr=subprocess.STDOUT).decode()
    output = re.sub('[0-9]\.[0-9]{2}%', '', output)
    fortunes = [x.strip() for x in output.splitlines()[1:]]
    return sorted(fortunes)


def cmd(send, msg, args):
    """Returns a fortune.
    Syntax: !fortune <list|module>
    """
    fortunes = get_list()
    try:
        if msg == 'list':
            send(" ".join(fortunes))
        else:
            if 'bofh' in basename(__file__) or 'excuse' in basename(__file__):
                mod = 'bofh-excuses'
            elif msg in fortunes or not msg:
                mod = msg
            else:
                send("%s is not a valid fortune module" % msg)
                return
            output = subprocess.check_output(['fortune', '-s', mod]).decode()
            for line in output.splitlines():
                send(line)
    except subprocess.CalledProcessError:
        send("fortune-mod is not installed!")
