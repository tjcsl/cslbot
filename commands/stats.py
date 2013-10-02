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
from random import choice
from helpers.command import Command, is_registered


def get_commands(cursor):
    rows = cursor.execute('SELECT DISTINCT command FROM commands').fetchall()
    return [row['command'] for row in rows]


def get_nicks(cursor, command):
    rows = cursor.execute('SELECT DISTINCT nick FROM commands WHERE command=?', (command,)).fetchall()
    return [row['nick'] for row in rows]


def get_totals(cursor, commands, name=None):
    totals = {}
    if name is None:
        for cmd in commands:
            totals[cmd] = cursor.execute('SELECT count() FROM commands WHERE command=?', (cmd,)).fetchone()[0]
    else:
        nicks = get_nicks(cursor, name)
        for nick in nicks:
            totals[nick] = cursor.execute('SELECT COUNT() FROM commands WHERE command=? AND nick=?', (name, nick)).fetchone()[0]
    return totals


@Command('stats', ['config', 'db'])
def cmd(send, msg, args):
    """Gets stats.
    Syntax: !stats <--high|--low|command>
    """
    cursor = args['db']
    commands = get_commands(cursor)
    if is_registered(msg):
        totals = get_totals(cursor, commands, msg)
        maxuser = sorted(totals, key=totals.get)
        if not maxuser:
            send("Nobody has used that command.")
        else:
            maxuser = maxuser[-1]
            send("%s is the most frequent user of %s with %d uses." % (maxuser, msg, totals[maxuser]))
    else:
        totals = get_totals(cursor, commands)
        match = re.match('--(.*)', msg)
        if match:
            sortedtotals = sorted(totals, key=totals.get)
            if match.group(1) == 'high':
                send('Most Used Commands:')
                high = list(reversed(sortedtotals))
                for x in range(0, 3):
                    if x < len(high):
                        send("%s: %s" % (high[x], totals[high[x]]))
            elif match.group(1) == 'low':
                send('Least Used Commands:')
                low = sortedtotals
                for x in range(0, 3):
                    if x < len(low):
                        send("%s: %s" % (low[x], totals[low[x]]))
            else:
                send("%s is not a valid flag" % match.group(1))
        elif msg:
            send("Invalid Command.")
        else:
            cmd = choice(list(totals.keys()))
            send("%s: %s" % (cmd, totals[cmd]))
