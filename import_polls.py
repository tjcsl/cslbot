#!/usr/bin/python3 -OO
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import sqlite3
import json
from os.path import dirname

polls = json.load(open(dirname(__file__) + "/data/polls"))
dbconn = sqlite3.connect(dirname(__file__) + "/db.sqlite")

cur = dbconn.cursor()

for poll in polls:
    active = poll['active']
    question = poll['question']
    votes = poll['votes']

    if active:
        active = 1
    else:
        active = 0

    cur.execute('INSERT INTO polls(question, active, deleted, rowid) VALUES (?,?,0,NULL)',
                (question, active))

    dbconn.commit()
    qid = cur.execute('SELECT id FROM polls WHERE question=? ORDER BY id DESC', (question,)).fetchone()[0]

    for nick, vote in votes.items():
        print(nick, vote)
        cur.execute('INSERT INTO poll_responses(qid, voter, response, id) VALUES(?,?,?,Null)', (qid, nick, vote))
    dbconn.commit()
