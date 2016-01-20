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

from random import choice

from ..helpers.command import Command


@Command('slap', ['handler', 'target', 'config'])
def cmd(send, msg, args):
    """Slap somebody.
    Syntax: {command} <nick> [for <reason>]
    """
    implements = ['the golden gate bridge', 'a large trout', 'a clue-by-four', 'a fresh haddock', 'moon', 'an Itanium', 'fwilson', 'a wombat']
    methods = ['around a bit', 'upside the head']
    if not msg:
        channel = args['target'] if args['target'] != 'private' else args['config']['core']['channel']
        with args['handler'].data_lock:
            users = list(args['handler'].channels[channel].users())
        slap = 'slaps %s %s with %s'
        send(slap % (choice(users), choice(methods), choice(implements)), 'action')
    else:
        reason = ''
        method = choice(methods)
        implement = ''
        msg = msg.split()
        slapee = msg[0]
        # Basic and stupid NLP!
        i = 1
        args = False
        while i < len(msg):
            if msg[i] == 'for':
                args = True
                if reason:
                    send("Invalid Syntax: You can only have one for clause!")
                    return
                i += 1
                while i < len(msg):
                    if msg[i] == 'with':
                        break
                    reason += " "
                    reason += msg[i]
                    i += 1
                reason = reason.strip()
            elif msg[i] == 'with':
                args = True
                if implement:
                    send("Invalid Synatx: You can only have one with clause!")
                    return
                i += 1
                while i < len(msg):
                    if msg[i] == 'for':
                        break
                    implement += msg[i]
                    implement += ' '
                    i += 1
                implement = implement.strip()
            elif not args:
                slapee += ' ' + msg[i]
            i += 1

        if not implement:
            implement = choice(implements)
        if reason:
            slap = 'slaps %s %s with %s for %s' % (slapee, method, implement, reason)
        else:
            slap = 'slaps %s %s with %s' % (slapee, method, implement)
        send(slap, 'action')
