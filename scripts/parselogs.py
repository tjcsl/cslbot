#!/usr/bin/python3 -OO
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

import argparse
from configparser import ConfigParser
from time import strftime, localtime
from os.path import dirname, exists
from os import makedirs
from sys import path

# HACK: allow sibling imports
path.append(dirname(__file__) + '/..')

from helpers.orm import Log
from helpers.sql import get_session

logs = {}

day = False


def get_id(config, outdir):
    outfile = "%s/.dbid" % outdir
    if not exists(outfile):
        return 0
    with open(outfile) as f:
        return int(f.read())


def save_id(outdir, new_id):
    if not exists(outdir):
        makedirs(outdir)
    with open('%s/.dbid' % outdir, 'w') as f:
        f.write(str(new_id))


def write_log(name, outdir, msg):
    global logs
    if name not in logs:
        outfile = "%s/%s.log" % (outdir, name)
        logs[name] = open(outfile, 'a')
    logs[name].write(msg)


def check_day(row, outdir, name):
    global day
    time = localtime(row.time)
    rowday = strftime('%d', time)
    if not day:
        day = rowday
        return
    if day != rowday:
        day = rowday
        log = strftime('New Day: %a, %b %d, %Y\n', time)
        write_log(name, outdir, log)


def gen_log(row):
    logtime = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
    nick = row.source.split('!')[0]
    if row.type == 'join':
        log = '%s --> %s (%s) has joined %s\n' % (logtime, nick, row.source, row.msg)
    elif row.type == 'part':
        log = '%s <-- %s (%s) has left %s\n' % (logtime, nick, row.source, row.msg)
    elif row.type == 'quit':
        log = '%s <-- %s (%s) has quit (%s)\n' % (logtime, nick, row.source, row.msg)
    elif row.type == 'kick':
        args = row.msg.split(',')
        log = '%s <-- %s has kicked %s (%s)\n' % (logtime, nick, args[0], args[1])
    elif row.type == 'action':
        log = '%s * %s %s\n' % (logtime, nick, row.msg)
    elif row.type == 'mode':
        log = '%s Mode %s [%s] by %s\n' % (logtime, row.target, row.msg, nick)
    elif row.type == 'nick':
        log = '%s -- %s is now know as %s\n' % (logtime, nick, row.msg)
    elif row.type == 'pubnotice':
        log = '%s Notice(%s): %s\n' % (logtime, nick, row.msg)
    elif row.type == 'privmsg' or row.type == 'pubmsg':
        if bool(row.flags & 1):
            nick = '@' + nick
        if bool(row.flags & 2):
            nick = '+' + nick
        log = '%s <%s> %s\n' % (logtime, nick, row.msg)
    else:
        raise Exception("Invalid type.")
    return log


def main(config, outdir):
    session = get_session(config)
    current_id = get_id(config, outdir)
    new_id = session.query(Log.id).order_by(Log.id.desc()).limit(1).scalar()
    save_id(outdir, new_id)
    for row in session.query(Log).filter(new_id > Log.id).filter(Log.id >= current_id).order_by(Log.id).all():
        check_day(row, outdir, config['core']['channel'])
        write_log(row.target, outdir, gen_log(row))
    for x in logs.values():
        x.close()


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open(dirname(__file__) + '/../config.cfg'))
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', help='The directory to write logs too.')
    args = parser.parse_args()
    main(config, args.outdir)
