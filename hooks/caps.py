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

from helpers.hook import Hook
from threading import Lock
import string

_caps = []
_caps_lock = Lock()


@Hook('caps', 'pubmsg', ['nick', 'do_kick', 'target', 'config'])
def handle(send, msg, args):
    """ Check for capslock abuse.

    | Check if a line is more than THRESHOLD percent uppercase.
    | If this is the second line in a row, kick the user.
    """
    # SHUT CAPS LOCK OFF, MORON

    if args['config']['feature'].getboolean('capskick'):
        nick = args['nick']
        THRESHOLD = 0.65
        text = "shutting caps lock off"
        upper = [i for i in msg if i in string.ascii_uppercase]
        if len(msg) == 0:
            return
        upper_ratio = len(upper) / len(msg.replace(' ', ''))
        if args['target'] != 'private':
            with _caps_lock:
                if upper_ratio > THRESHOLD and len(msg) > 20:
                    if nick in _caps:
                        args['do_kick'](args['target'], nick, text)
                        _caps.remove(nick)
                    else:
                        _caps.append(nick)
                elif nick in _caps:
                    _caps.remove(nick)
