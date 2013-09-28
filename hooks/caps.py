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

from helpers.hook import Hook
import string

_caps = []


@Hook(types=['pubmsg'], args=['nick', 'do_kick', 'target'])
def handle(send, msg, args):
    """ Check for capslock abuse.

    | Check if a line is more than :const:`THRESHOLD` percent uppercase.
    | If this is the first line, warn the user.
    | If this is the second line in a row, kick the user.
    """
    # SHUT CAPS LOCK OFF, MORON
    global _caps

    nick = args['nick']
    THRESHOLD = 0.65
    text = "shutting caps lock off"
    upper = [i for i in msg if i in string.ascii_uppercase]
    upper_ratio = len(upper) / len(msg)
    if args['target'] != 'private':
        if upper_ratio > THRESHOLD and len(msg) > 6:
            if nick in _caps:
                args['do_kick'](args['target'], nick, text)
                _caps.remove(nick)
            else:
                _caps.append(nick)
        elif nick in _caps:
            _caps.remove(nick)
