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
from random import randint
from helpers.command import Command


@Command('score', ['config', 'db', 'botnick'])
def cmd(send, msg, args):
    """Gets scores.
    Syntax: !score <--high|--low|nick>
    """
    cursor = args['db']
    match = re.match('--(.+)', msg)
    if match:
        if match.group(1) == 'high':
            data = cursor.execute("SELECT nick,score FROM scores ORDER BY score DESC LIMIT 3").fetchall()
            send('High Scores:')
            for x in data:
                send("%s: %s" % (x['nick'], x['score']))
        elif match.group(1) == 'low':
            data = cursor.execute("SELECT nick,score FROM scores ORDER BY score LIMIT 3").fetchall()
            send('Low Scores:')
            for x in data:
                send("%s: %s" % (x['nick'], x['score']))
        else:
            send("%s is not a valid flag" % match.group(1))
        return
    match = re.match('(%s+)' % args['config']['core']['nickregex'], msg)
    if match:
        name = match.group(1).lower()
        score = cursor.execute("SELECT score FROM scores WHERE nick=?", (name,)).fetchone()
        if score is not None:
            score = score[0]
            if name == args['botnick'].lower():
                output = 'has %s points! :)' % score
                send(output, 'action')
            else:
                send("%s has %i points!" % (name, score))
        else:
            send("Nobody cares about %s" % name)
    elif msg:
        send("Invalid nick")
    else:
        count = cursor.execute("SELECT count(*) FROM scores").fetchone()
        if count is None or count[0] == 0:
            send("Nobody cares about anything =(")
        else:
            if count[0] == 1:
                randid = 1
            else:
                randid = randint(1, count[0])
            query = cursor.execute("SELECT nick,score FROM scores WHERE id=?", (randid,)).fetchone()
            send("%s has %i points!" % (query[0], query[1]))
