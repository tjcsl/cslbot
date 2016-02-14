# -*- coding: utf-8 -*-
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

from ..helpers.command import Command
from ..helpers.misc import do_nuke


@Command('microwave', ['nick', 'botnick', 'handler', 'is_admin', 'target', 'config'], limit=5)
def cmd(send, msg, args):
    """Microwaves something.

    Syntax: {command} <level> <target>

    """
    nick = args['nick']
    channel = args['target'] if args['target'] != 'private' else args['config']['core']['channel']
    levels = {1: 'Whirr...',
              2: 'Vrrm...',
              3: 'Zzzzhhhh...',
              4: 'SHFRRRRM...',
              5: 'GEEEEZZSH...',
              6: 'PLAAAAIIID...',
              7: 'KKKRRRAAKKKAAKRAKKGGARGHGIZZZZ...',
              8: 'Nuke',
              9: 'nneeeaaaooowwwwww..... BOOOOOSH BLAM KABOOM',
              10: 'ssh root@remote.tjhsst.edu rm -rf ~%s'}
    if not msg:
        send('What to microwave?')
        return
    match = re.match('(-?[0-9]*) (.*)', msg)
    if not match:
        send('Power level?')
    else:
        level = int(match.group(1))
        target = match.group(2)
        if level > 10:
            send('Aborting to prevent extinction of human race.')
            return
        if level < 1:
            send('Anti-matter not yet implemented.')
            return
        if level > 7:
            if not args['is_admin'](nick):
                send("I'm sorry. Nukes are a admin-only feature")
                return
            elif msg == args['botnick']:
                send("Sorry, Self-Nuking is disabled pending aquisition of a Lead-Lined Fridge.")
            else:
                with args['handler'].data_lock:
                    if target not in args['handler'].channels[channel].users():
                        send("I'm sorry. Anonymous Nuking is not allowed")
                        return

        msg = levels[1]
        for i in range(2, level + 1):
            if i < 8:
                msg += ' ' + levels[i]
        send(msg)
        if level >= 8:
            do_nuke(args['handler'].connection, nick, target, channel)
        if level >= 9:
            send(levels[9])
        if level == 10:
            send(levels[10] % target)
        send('Ding, your %s is ready.' % target)
