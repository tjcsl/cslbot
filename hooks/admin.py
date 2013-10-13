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

import re
from helpers.hook import Hook


@Hook(types=['privnotice'], args=['channels', 'config', 'do_kick', 'handler', 'nick', 'target'])
def handle(send, msg, args):
    """Handle admin verification responses from NickServ.

    | If someone other than NickServ is trying to become a admin,
    | kick them.
    | If NickServ tells us that the nick is authed, mark it as verified.
    """
    match = re.match("(.*) ACC ([0-3])", msg)
    if not match:
        return
    if args['nick'] != 'NickServ':
        if args['nick'] in list(args['channels'][args['config']['core']['channel']].users()):
            send("Attemped admin abuse by %s" % args['nick'], target=args['config']['core']['channel'])
            args['do_kick'](send, args['target'], args['nick'], "imposter")
    elif int(match.group(2)) == 3:
        args['handler'].admins[match.group(1)] = True
