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
from time import time
from os.path import dirname


class Sql():

    def __init__(self):
        """ Set everything up

        | dbconn is a connection to a sqlite database.
        """
        dbfile = dirname(__file__) + '/db.sqlite'
        self.db = sqlite3.connect(dbfile)
        self.setup_db()

    def log(self, source, target, operator, msg, msg_type):
        """ Logs a message to the database

        | source: The source of the message.
        | target: The target of the message.
        | operator: Is the user a operator?
        | msg: The text of the message.
        | msg: The type of message.
        | time: The current time (Unix Epoch).
        """
        self.db.execute('INSERT INTO log VALUES(?,?,?,?,?,?)',
                        (source, target, operator, msg, msg_type, time()))
        self.db.commit()

    def get(self):
        return self.db.cursor()

    def setup_db(self):
        """ Sets up the database.
        """
        self.db.execute('CREATE TABLE IF NOT EXISTS log(source TEXT, target TEXT, operator INTEGER, msg TEXT, type TEXT, time INTEGER)')
