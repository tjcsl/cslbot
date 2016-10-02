# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import multiprocessing
import re

import sre_constants

from ..helpers.command import Command
from ..helpers.exception import CommandFailedException
from ..helpers.orm import Log
from ..helpers.misc import escape


def get_log(conn, target, user):
    query = conn.query(Log).filter((Log.type == 'privmsg') | (Log.type == 'pubmsg') | (Log.type == 'action'),
                                   Log.target == target).order_by(Log.time.desc())
    if user is None:
        return query.offset(1).limit(500).all()
    else:
        return query.filter(Log.source.ilike(user)).limit(500).all()


def get_modifiers(msg, nick, nickregex):
    mods = {'ignorecase': False, 'allnicks': False, 'nick': nick}
    if not msg:
        return mods
    elif msg == "i":
        mods['ignorecase'] = True
    elif msg == "g":
        mods['allnicks'] = True
        mods['nick'] = None
    elif msg == "ig" or msg == "gi":
        mods['allnicks'] = True
        mods['ignorecase'] = True
        mods['nick'] = None
    elif re.match(nickregex, msg):
        mods['nick'] = escape(msg)
    else:
        return None
    return mods


def do_replace(log, config, char, regex, replacement):
    startchars = [config['cmdchar']]
    startchars.extend(config['altcmdchars'].split(','))
    # pre-generate the possible start strings
    starttuple = tuple(['%ss%s' % (startchar.strip(), char) for startchar in startchars])
    for line in log:
        # ignore previous !s calls.
        if line.msg.startswith(starttuple):
            continue
        if line.msg.startswith('%s: s%s' % (config['nick'], char)):
            continue
        if regex.search(line.msg):
            output = regex.sub(replacement, line.msg)
            if line.type == 'action':
                return "correction: * %s %s" % (line.source, output)
            elif line.type != 'mode':
                return "%s actually meant: %s" % (line.source, output)


@Command('s', ['db', 'type', 'nick', 'config', 'botnick', 'target', 'handler'])
def cmd(send, msg, args):
    """Corrects a previous message.

    Syntax: {command}/<msg>/<replacement>/<ig|nick>

    """
    if not msg:
        send("Invalid Syntax.")
        return
    char = msg[0]
    msg = [x.replace(r'\/', '/') for x in re.split(r'(?<!\\)\%s' % char, msg[1:], maxsplit=2)]
    # fix for people who forget a trailing slash
    if len(msg) == 2 and args['config']['feature'].getboolean('lazyregex'):
        msg.append('')
    # not a valid sed statement.
    if not msg or len(msg) < 3:
        send("Invalid Syntax.")
        return
    if args['type'] == 'privmsg':
        send("Don't worry, %s is not a grammar Nazi." % args['botnick'])
        return
    string = msg[0]
    replacement = msg[1]
    modifiers = get_modifiers(msg[2], args['nick'], args['config']['core']['nickregex'])
    if modifiers is None:
        send("Invalid modifiers.")
        return

    try:
        regex = re.compile(string, re.IGNORECASE) if modifiers['ignorecase'] else re.compile(string)
        log = get_log(args['db'], args['target'], modifiers['nick'])
        workers = args['handler'].workers
        result = workers.run_pool(do_replace, [log, args['config']['core'], char, regex, replacement])
        try:
            msg = result.get(5)
        except multiprocessing.TimeoutError:
            workers.restart_pool()
            send("Sed regex timed out.")
            return
        if msg:
            send(msg)
        else:
            send("No match found.")
    except sre_constants.error as ex:
        raise CommandFailedException(ex)
