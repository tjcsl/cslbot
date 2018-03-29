# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from datetime import datetime

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Stopwatches


def create_stopwatch(args):
    row = Stopwatches(time=datetime.now())
    args.session.add(row)
    args.session.flush()
    return "Created new stopwatch with ID %d" % row.id


def get_elapsed(session, sw):
    stopwatch = session.query(Stopwatches).get(sw)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    etime = stopwatch.elapsed
    if stopwatch.active == 1:
        etime = datetime.now() - stopwatch.time
    return str(etime)


def stop_stopwatch(args):
    stopwatch = args.session.query(Stopwatches).get(args.id)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    if stopwatch.active == 0:
        return "That stopwatch is already stopped!"
    etime = datetime.now() - stopwatch.time
    stopwatch.elapsed = etime.total_seconds()
    stopwatch.active = 0
    return "Stopwatch stopped at %s" % get_elapsed(args.session, args.id)


def delete_stopwatch(args):
    if not args.isadmin:
        return "Nope, not gonna do it!"
    stopwatch = args.session.query(Stopwatches).get(args.id)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    if stopwatch.active == 1:
        return "That stopwatch is currently running!"
    args.session.delete(stopwatch)
    return "Stopwatch deleted!"


def resume_stopwatch(args):
    stopwatch = args.session.query(Stopwatches).get(args.id)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    if stopwatch.active == 1:
        return "That stopwatch is not paused!"
    stopwatch.active = 1
    stopwatch.time = datetime.now()
    return "Stopwatch resumed!"


def list_stopwatch(args):
    active = args.session.query(Stopwatches).filter(Stopwatches.active == 1).order_by(Stopwatches.id).all()
    paused = args.session.query(Stopwatches).filter(Stopwatches.active == 0).order_by(Stopwatches.id).all()
    for x in active:
        args.send('Active stopwatch #%d started at %s' % (x.id, x.time), target=args.nick)
    for x in paused:
        args.send('Paused stopwatch #%d started at %s time elapsed %d' % (x.id, x.time, x.elapsed), target=args.nick)
    return "%d active and %d paused stopwatches." % (len(active), len(paused))


def get_stopwatch(args):
    stopwatch = args.session.query(Stopwatches).get(args.id)
    if stopwatch is None:
        return "Invalid ID!"
    status = "Active" if stopwatch.active == 1 else "Paused"
    return "%s %s" % (status, get_elapsed(args.session, args.id))


@Command(['stopwatch', 'sw'], ['config', 'db', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Start/stops/resume/get stopwatch
    Syntax: {command} <start|stop|resume|delete|get|list>
    """

    parser = arguments.ArgParser(args['config'])
    parser.set_defaults(session=args['db'])
    subparser = parser.add_subparsers()
    start_parser = subparser.add_parser('start')
    start_parser.set_defaults(func=create_stopwatch)
    stop_parser = subparser.add_parser('stop')
    stop_parser.add_argument('id', type=int)
    stop_parser.set_defaults(func=stop_stopwatch)
    resume_parser = subparser.add_parser('resume')
    resume_parser.add_argument('id', type=int)
    resume_parser.set_defaults(func=resume_stopwatch)
    delete_parser = subparser.add_parser('delete')
    delete_parser.add_argument('id', type=int)
    delete_parser.set_defaults(func=delete_stopwatch, isadmin=args['is_admin'](args['nick']))
    get_parser = subparser.add_parser('get')
    get_parser.add_argument('id', type=int)
    get_parser.set_defaults(func=get_stopwatch)
    list_parser = subparser.add_parser('list')
    list_parser.set_defaults(func=list_stopwatch, nick=args['nick'], send=send)

    if not msg:
        send("Please specify a command.")
        return

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    send(cmdargs.func(cmdargs))
