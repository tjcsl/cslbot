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

from ..helpers.hook import Hook
from ..helpers.orm import Scores
import re


@Hook('scores', ['pubmsg', 'privmsg', 'action'], ['nick', 'config', 'type', 'db', 'abuse'])
def handle(send, msg, args):
    """ Handles scores

    | If it's a ++ add one point unless the user is trying to promote
    | themselves.
    | Otherwise substract one point.
    """
    session = args['db']
    matches = re.findall(r"\b(?<!-)(%s{2,16})(\+\+|--)" % args['config']['core']['nickregex'], msg)
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
        row = session.query(Scores).filter(Scores.nick == name).first()
        if row is None:
            session.add(Scores(score=score, nick=name))
            session.commit()
        else:
            row.score += score
            session.commit()
