#!/usr/bin/env python3
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

from sys import path
from os.path import dirname, exists, join

# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    path.insert(0, join(dirname(__file__), '..'))
import argparse
import configparser
import fcntl
from time import strftime, localtime
from os import makedirs

from cslbot.helpers.orm import Log
from cslbot.helpers.sql import get_session

logs = {}

day = False


def get_id(outdir):
    outfile = "%s/.dbid" % outdir
    if not exists(outfile):
        return 0
    with open(outfile) as f:
        return int(f.read())


def save_id(outdir, new_id):
    with open('%s/.dbid' % outdir, 'w') as f:
        f.write(str(new_id) + '\n')


def write_log(name, outdir, msg):
    if name not in logs:
        outfile = "%s/%s.log" % (outdir, name)
        logs[name] = open(outfile, 'a')
    logs[name].write(msg + '\n')


def check_day(row, outdir, name):
    # FIXME: don't use a global variable.
    global day
    time = localtime(row.time)
    rowday = strftime('%d', time)
    if not day:
        day = rowday
        return
    if day != rowday:
        day = rowday
        log = strftime('New Day: %a, %b %d, %Y', time)
        write_log(name, outdir, log)


def gen_log(row):
    logtime = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
    nick = row.source.split('!')[0]
    if row.type == 'join':
        log = '%s --> %s (%s) has joined %s' % (logtime, nick, row.source, row.target)
    elif row.type == 'part':
        log = '%s <-- %s (%s) has left %s' % (logtime, nick, row.source, row.target)
        if row.msg:
            log = "%s (%s)" % (log, row.msg)
    elif row.type == 'quit':
        log = '%s <-- %s (%s) has quit (%s)' % (logtime, nick, row.source, row.msg)
    elif row.type == 'kick':
        args = row.msg.split()
        log = '%s <-- %s has kicked %s (%s)' % (logtime, nick, args[0], " ".join(args[1:]))
    elif row.type == 'action':
        log = '%s * %s %s' % (logtime, nick, row.msg)
    elif row.type == 'mode':
        log = '%s Mode %s [%s] by %s' % (logtime, row.target, row.msg, nick)
    elif row.type == 'nick':
        log = '%s -- %s is now known as %s' % (logtime, nick, row.msg)
    elif row.type == 'topic':
        # FIXME: keep track of the old topic
        log = '%s %s has changed topic for %s to "%s"' % (logtime, nick, row.target, row.msg)
    elif row.type in ['pubnotice', 'privnotice']:
        log = '%s Notice(%s): %s' % (logtime, nick, row.msg)
    elif row.type in ['privmsg', 'pubmsg']:
        if bool(row.flags & 1):
            nick = '@' + nick
        if bool(row.flags & 2):
            nick = '+' + nick
        log = '%s <%s> %s' % (logtime, nick, row.msg)
    else:
        raise Exception("Invalid type %s." % row.type)
    return log


def main(confdir="/etc/cslbot"):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    session = get_session(config)()
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', help='The directory to write logs too.')
    cmdargs = parser.parse_args()
    if not exists(cmdargs.outdir):
        makedirs(cmdargs.outdir)
    lockfile = open('%s/.lock' % cmdargs.outdir, 'w')
    fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    current_id = get_id(cmdargs.outdir)
    new_id = session.query(Log.id).order_by(Log.id.desc()).limit(1).scalar()
    # Don't die on empty log table.
    if new_id is None:
        new_id = 0
    save_id(cmdargs.outdir, new_id)
    for row in session.query(Log).filter(new_id >= Log.id).filter(Log.id > current_id).order_by(Log.time, Log.id).all():
        check_day(row, cmdargs.outdir, config['core']['channel'])
        write_log(row.target, cmdargs.outdir, gen_log(row))
    for x in logs.values():
        x.close()
    fcntl.lockf(lockfile, fcntl.LOCK_UN)
    lockfile.close()


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(join(dirname(__file__), '..'))
