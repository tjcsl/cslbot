#!/usr/bin/python3 -OO
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

import argparse
import sqlite3
from time import strftime, localtime
from os.path import dirname

logs = {}


def write_log(name, outdir, msg):
    if name not in logs:
        outfile = "%s/%s.log" % (outdir, name)
        logs[name] = open(outfile, 'w')
    logs[name].write(msg)


def gen_log(row):
    logtime = strftime('%H:%M:%S', localtime(row['time']))
    nick = row['source'].split('!')[0]
    if row['type'] == 'join':
        log = '%s --> %s (%s) has joined %s\n' % (logtime, nick, row['source'], row['msg'])
    elif row['type'] == 'part':
        log = '%s <-- %s (%s) has left %s\n' % (logtime, nick, row['source'], row['msg'])
    elif row['type'] == 'quit':
        log = '%s <-- %s (%s) has quit (%s)\n' % (logtime, nick, row['source'], row['msg'])
    elif row['type'] == 'action':
        log = '%s * %s %s\n' % (logtime, nick, row['msg'])
    elif row['type'] == 'mode':
        log = '%s Mode %s [%s] by %s\n' % (logtime, row['target'], row['msg'], nick)
    elif row['type'] == 'nick':
        log = '%s -- %s is now know as %s\n' % (logtime, nick, row['msg'])
    elif row['type'] == 'pubnotice':
        log = '%s Notice(%s): %s\n' % (logtime, nick, row['msg'])
    elif row['type'] == 'privmsg' or row['type'] == 'pubmsg':
        nick = '@' + nick if row['operator'] else nick
        log = '%s <%s> %s\n' % (logtime, nick, row['msg'])
    else:
        log = row['type'] + '\n'
    return log


def main(outdir):
    dbname = dirname(__file__) + "/log.sqlite"
    db = sqlite3.connect(dbname)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM log")
    rows = cursor.fetchall()
    for row in rows:
        write_log(row['target'], outdir, gen_log(row))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', help='The directory to write logs too.')
    args = parser.parse_args()
    main(args.outdir)
