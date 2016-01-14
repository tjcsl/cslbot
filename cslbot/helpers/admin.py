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

import re
from datetime import datetime


def set_admin(msg, handler):
    """Handle admin verification responses from NickServ.

    | If NickServ tells us that the nick is authed, mark it as verified.
    """
    if handler.config['feature']['servicestype'] == "ircservices":
        match = re.match("STATUS (.*) ([0-3])", msg)
    elif handler.config['feature']['servicestype'] == "atheme":
        match = re.match("(.*) ACC ([0-3])", msg)
    if match:
        status = int(match.group(2))
        nick = match.group(1)
        if status == 3:
            handler.admins[nick] = datetime.now()
