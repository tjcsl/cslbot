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

from helpers.hook import Hook
import re


@Hook(['pubmsg', 'privmsg'], ['nick', 'config', 'type', 'db', 'abuse'])
def handle(send, msg, args):
    """ Handles scores

    | If it's a ++ add one point unless the user is trying to promote
    | themselves.
    | Otherwise substract one point.
    """
    matches = re.findall(r"(%s{2,})(\+\+|--)" % args['config']['core']['nickregex'], msg)
    if not matches:
        return
    if args['type'] == 'privmsg':
        send('Hey, no points in private messages!')
        return
    for match in matches:
        # limit to 5 score changes per minute
        if args['abuse'](args['nick'], 5, 'scores'):
            return
        name, direction = match[0].lower(), match[1]
        if direction == "++":
            score = 1
            if name == args['nick'].lower():
                send("%s: No self promotion! You lose 10 points." % args['nick'])
                score = -10
        else:
            score = -1
        #TODO: maybe we can do this with INSERT OR REPLACE?
        cursor = args['db'].get()
        if cursor.execute("SELECT COUNT(1) FROM scores WHERE nick=%s", (name,)).scalar() is None:
            cursor.execute("INSERT INTO scores VALUES(%s,%s)", (name, score))
        else:
            cursor.execute("UPDATE scores SET score=score+%s WHERE nick=%s", (score, name))
