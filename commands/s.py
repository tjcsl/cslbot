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
from helpers.command import Command


#FIXME: combine w/ reverse.py
def get_log(conn, target, user):
    if user is None:
        cursor = conn.execute('SELECT msg,type,source FROM log WHERE target=? ORDER BY time DESC LIMIT 50', (target,))
        # Don't parrot back the !s call.
        cursor.fetchone()
    else:
        cursor = conn.execute('SELECT msg,type,source FROM log WHERE source=? AND target=? ORDER BY time DESC LIMIT 50', (user, target))
    return cursor.fetchall()


def get_modifiers(msg, nick):
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
    else:
        mods['nick'] = msg
    return mods


@Command('s', ['db', 'type', 'nick', 'config', 'botnick', 'target'])
def cmd(send, msg, args):
    """Corrects a previous message.
    Syntax: !s/<msg>/<replacement>/<ig|nick>
    """
    if not msg:
        send("Invalid Syntax.")
        return
    conn = args['db'].get()
    char = msg[0]
    msg = msg[1:].split(char)
    #fix for people who forget a trailing slash
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
    modifiers = get_modifiers(msg[2], args['nick'])
    regex = re.compile(string, re.IGNORECASE) if modifiers['ignorecase'] else re.compile(string)
    log = get_log(conn, args['target'], modifiers['nick'])

    for line in log:
        # ignore previous !s calls.
        if line['msg'].startswith('%ss%s' % (args['config']['core']['cmdchar'], char)):
            continue
        if line['msg'].startswith('%s: s%s' % (args['config']['core']['nick'], char)):
            continue
        if regex.search(line['msg']):
            output = regex.sub(replacement, line['msg'])
            if len(output) > 256:
                output = output[:253] + "..."
            if line['type'] == 'action':
                send("correction: * %s %s" % (line['source'], output))
            elif line['type'] != 'mode':
                send("%s actually meant: %s" % (line['source'], output))
            return
    send("No match found.")
