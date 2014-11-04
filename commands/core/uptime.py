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

from time import time
from datetime import timedelta
from helpers.command import Command


@Command('uptime', ['handler'])
def cmd(send, msg, args):
    """Shows the bot's uptime.
    Syntax: !uptime
    """
    curr = time()
    uptime = args['handler'].uptime
    starttime = curr - uptime['start']
    reloaded = curr - uptime['reloaded']
    send("Time since start: %s" % timedelta(seconds=starttime))
    send("Time since reload: %s" % timedelta(seconds=reloaded))
