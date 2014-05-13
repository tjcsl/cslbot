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

import re
from random import randint
from helpers.orm import Scores
from helpers.command import Command


def pluralize(s, n):
    if n == 1:
        return s
    else:
        return s + 's'


@Command('score', ['config', 'db', 'botnick'])
def cmd(send, msg, args):
    """Gets scores.
    Syntax: !score <--high|--low|nick>
    """
    if not args['config']['feature'].getboolean('hooks'):
        send("Hooks are disabled, and this command depends on hooks. Please contact the bot admin(s).")
        return
    session = args['db']
    match = re.match('--(.+)', msg)
    if match:
        if match.group(1) == 'high':
            data = session.query(Scores).order_by(Scores.score.desc()).limit(3).all()
            send('High Scores:')
            for x in data:
                send("%s: %s" % (x.nick, x.score))
        elif match.group(1) == 'low':
            data = session.query(Scores).order_by(Scores.score).limit(3).all()
            send('Low Scores:')
            for x in data:
                send("%s: %s" % (x.nick, x.score))
        else:
            send("%s is not a valid flag" % match.group(1))
        return
    matches = re.findall('(%s+)' % args['config']['core']['nickregex'], msg)
    if matches:
        for match in matches:
            name = match.lower()
            if name == 'c':
                send("We all know you love C better than anything else, so why rub it in?")
                return
            score = session.query(Scores).filter(Scores.nick == name).scalar()
            if score is not None:
                if name == args['botnick'].lower():
                    output = 'has %s %s! :)' % (score.score, pluralize('point', score.score))
                    send(output, 'action'
                else:
                    send("%s has %i %s!" % (name, score.score, pluralize('point', score.score)))
            else:
                send("Nobody cares about %s" % name)
    elif msg:
        send("Invalid nick")
    else:
        count = session.query(Scores).count()
        if count == 0:
            send("Nobody cares about anything =(")
        else:
            randid = randint(1, count)
            query = session.query(Scores).get(randid)
            send("%s has %i points!" % (query.nick, query.score))
