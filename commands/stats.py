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

from helpers.command import Command


def get_commands(cursor):
    rows = cursor.execute('SELECT DISTINCT command FROM commands').fetchall()
    return [row['command'] for row in rows]


def get_totals(cursor, commands):
    totals = {}
    for cmd in commands:
        totals[cmd] = cursor.execute('SELECT count(nick) FROM commands WHERE command=?', (cmd,)).fetchone()[0]
    return totals


@Command('stats', ['config', 'db', 'botnick'])
def cmd(send, msg, args):
    """Gets scores.
    Syntax: !score <--high|--low|nick>
    """
    cursor = args['db']
    commands = get_commands(cursor)
    totals = get_totals(cursor, commands)
    send(str(totals))
    #match = re.match('(%s+)' % args['config']['core']['nickregex'], msg)
