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

from random import choice
from sqlalchemy import func
from ..helpers.orm import Commands
from ..helpers import arguments
from ..helpers.command import Command, is_registered


def get_commands(session):
    rows = session.query(Commands.command).distinct().all()
    return [row.command for row in rows]


def get_command_totals(session, commands):
    rows = session.query(Commands.command, func.count(Commands.command)).group_by(Commands.command).all()
    return {x[0]: x[1] for x in rows}


def get_nick_totals(session, command=None):
    query = session.query(Commands.nick, func.count(Commands.nick)).group_by(Commands.nick)
    if command is not None:
        query = query.filter(Commands.command == command)
    return {x[0]: x[1] for x in query.all()}


@Command('stats', ['config', 'db'])
def cmd(send, msg, args):
    """Gets stats.
    Syntax: {command} <--high|--low|--userhigh|--nick <nick>|command>
    """
    parser = arguments.ArgParser(args['config'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--high', action='store_true')
    group.add_argument('--low', action='store_true')
    group.add_argument('--userhigh', action='store_true')
    group.add_argument('--nick', action=arguments.NickParser)
    group.add_argument('command', nargs='?')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    session = args['db']
    commands = get_commands(session)
    totals = get_command_totals(session, commands)
    sortedtotals = sorted(totals, key=totals.get)
    if is_registered(cmdargs.command):
        nicktotals = get_nick_totals(session, cmdargs.command)
        maxuser = sorted(nicktotals, key=nicktotals.get)
        if not maxuser:
            send("Nobody has used that command.")
        else:
            maxuser = maxuser[-1]
            send("%s is the most frequent user of %s with %d out of %d uses." % (maxuser, cmdargs.command, nicktotals[maxuser], totals[cmdargs.command]))
    elif cmdargs.command and not is_registered(cmdargs.command):
        send("Command %s not found." % cmdargs.command)
    elif cmdargs.high:
        send('Most Used Commands:')
        high = list(reversed(sortedtotals))
        for x in range(3):
            if x < len(high):
                send("%s: %s" % (high[x], totals[high[x]]))
    elif cmdargs.low:
        send('Least Used Commands:')
        low = sortedtotals
        for x in range(3):
            if x < len(low):
                send("%s: %s" % (low[x], totals[low[x]]))
    elif cmdargs.userhigh:
        totals = get_nick_totals(session)
        sortedtotals = sorted(totals, key=totals.get)
        high = list(reversed(sortedtotals))
        send('Most active bot users:')
        for x in range(3):
            if x < len(high):
                send("%s: %s" % (high[x], totals[high[x]]))
    elif cmdargs.nick:
        totals = get_nick_totals(session)
        if cmdargs.nick not in totals.keys():
            send("%s has never used a bot command." % cmdargs.nick)
        else:
            send("%s has used %d bot commands." % (cmdargs.nick, totals[cmdargs.nick]))
    else:
        command = choice(list(totals.keys()))
        send("%s has been used %s times." % (command, totals[command]))
