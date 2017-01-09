# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import datetime

import dateutil
import dateutil.parser

from ..helpers import arguments
from ..helpers.command import Command


@Command(['timeuntil', 'timetill'], ['config'])
def cmd(send, msg, args):
    """Reports the difference between now and some specified time.

    Syntax: {command} <time>

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('date', nargs='*', action=arguments.DateParser)
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.date:
        send("Time until when?")
        return
    delta = dateutil.relativedelta.relativedelta(cmdargs.date, datetime.datetime.now())
    diff = "%s is " % cmdargs.date.strftime("%x")
    if delta.years:
        diff += "%d years " % (delta.years)
    if delta.months:
        diff += "%d months " % (delta.months)
    if delta.days:
        diff += "%d days " % (delta.days)
    if delta.hours:
        diff += "%d hours " % (delta.hours)
    if delta.minutes:
        diff += "%d minutes " % (delta.minutes)
    if delta.seconds:
        diff += "%d seconds " % (delta.seconds)
    diff += "away"
    send(diff)
