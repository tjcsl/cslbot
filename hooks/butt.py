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

from random import random
from helpers.hook import Hook


@Hook('butt', 'pubmsg', ['type', 'nick'])
def handle(send, msg, args):
    if "the cloud" in msg:
        msg = msg.replace("the cloud", "my butt")
    elif "cloud" in msg:
        msg = msg.replace("cloud", "butt")
    else:
        return
    # make it more random.
    if random() > 0.005:
        return
    if args['type'] == 'pubmsg':
        send("%s actually meant: %s" % (args['nick'], msg))
    else:
        send("correction: * %s %s" % (args['nick'], msg))
