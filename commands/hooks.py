
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

from helpers.hook import get_known_hooks
from helpers.command import Command


@Command('hooks', ['nick', 'connection'])
def cmd(send, msg, args):
    """Lists loaded hooks
    Syntax: !hooks
    """
    hooks = get_known_hooks()
    num = int(len(hooks) / 2)
    hooklist1 = ' '.join([x.get_func_location() for x in hooks[:num]])
    hooklist2 = ' '.join([x.get_func_location() for x in hooks[num:]])
    args['connection'].privmsg(args['nick'], 'Loaded hooks: %s' % (hooklist1))
    args['connection'].privmsg(args['nick'], '%s' % (hooklist2))
