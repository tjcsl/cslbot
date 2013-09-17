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

import time

args=['db']

def pretty_div(num, div, m):
    return (num // div) % m


def pretty_elapsed(time):
    ts = ""
    if time > 24 * 7 * 3600:
        ts = ts + " " + pretty_div(time, 24 * 7 * 3600, 52) + " weeks"
    if time > 24 * 3600:
        ts = ts + " " + pretty_div(time, 24 * 3600, 7) + " days"
    if time > 3600:
        ts = ts + " " + pretty_div(time, 3600, 24) + " hours"
    if time > 60:
        ts = ts + " " + pretty_div(time, 60, 60) + " minutes"
    if time > 1:
        ts = ts + " " + pretty_div(time, 1, 1) + " seconds"
    ts = ts + " " + ((time % 1) * 1000) + " milliseconds"

def create_sw(cursor):
    cursor.execute("INSERT INTO stopwatches(id,elapsed,active,time) VALUES(NULL,0,1,?)", (time.time(),))
    cid = cursor.execute("SELECT max(id) FROM stopwatches").fetchall()[0][0]
    return "Created new stopwatch. ID: %d" % cid

def get_elapsed(cursor, sw):
    if not sw:
        return "You need to pass a stopwatch ID to !stopwatch get"
    if not(sw.is_digit()):
        return "Invalid ID!"
    query_result = cursor.execute("SELECT elapsed,time,active FROM stopwatches WHERE id=?", int(sw))
    elapsed = query_result[0]
    etime = 0
    if query_result[2] == 1:
        print(query_result[1])
        etime = time.time() - query_result[1]
    return pretty_elapsed(etime)

def cmd(send, msg, args):
    """Start/stops/resume/get stopwatch
    !stopwatch [start] Start new stopwatch
    !stopwatch [stop|resume] [id] Resumes stopwatch id or the most recently created stopwatch
    !stopwatch [get] Gets the time elapsed for stopwatch
    """

    command=msg.split(' ')[0]
    msg = msg.split(' ')[1:]
    cursor = args['db']
    if command == "start":
        send(create_sw(cursor))
    elif command == "get":
        send(get_elapsed(cursor, msg))
