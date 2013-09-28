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

import socket
from urllib.request import urlopen
from bs4 import BeautifulSoup
from helpers.command import Command


@Command('fweather')
def cmd(send, msg, args):
    """Gets the F***ING weather!
    Syntax: !fweather <location>
    """
    try:
        html = urlopen('http://thefuckingweather.com/?where=' + msg.replace(' ', '%20'), timeout=5).read()
        soup = BeautifulSoup(html)
        temp, remark, flavor = soup.findAll('p')
        send((temp.contents[0].contents[0] + ' F? ' + remark.contents[0]).replace("FUCK", "FSCK"))
    except ValueError:
        send('NO FSCKING RESULTS.')
    except socket.timeout:
        send('CONNECTION TIMED THE FSCK OUT.')
