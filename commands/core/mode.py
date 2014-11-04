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

from helpers.command import Command


def set_mode(args, mode):
    if not mode:
        return "What mode?"
    if args['target'] == 'private':
        return "Modes don't work in a PM!"
    if not args['is_admin'](args['nick']):
        return "Admins only"
    if args['botnick'] not in list(args['handler'].channels[args['target']].opers()):
        return "Bot must be opped"
    args['handler'].connection.mode(args['target'], " %s" % mode)
    return ""


@Command('mode', ['nick', 'is_admin', 'handler', 'botnick', 'target'])
def cmd(send, msg, args):
    """Sets a mode.
    Syntax: !mode <mode>
    """
    send(set_mode(args, msg))
