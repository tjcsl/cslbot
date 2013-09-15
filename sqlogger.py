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


class Logger():

    def __init__(self, dbfile):
        """ Set everything up

        | dbconn is a connection to a database. Currently only sqlite is
        |   supported
        """
        self.db = sqlite3.connect(dbfile)
        self.verify_db()

    def log(self, source, target, operator, msg, msg_type):
        """ Logs a message to the database

        | source: The source of the message.
        | target: The target of the message.
        | operator: Is the user a operator?
        | msg: The text of the message.
        | msg: The type of message. Valid types are
        |   - action - /me, etc.
        |   - join - channel joins
        |   - part - channel parts
        |   - quit - server quits
        |   - kick - channel kicks
        |   - mode - channel mode changes
        | time: The current time (Unix Epoch).
        """
        self.db.execute('INSERT INTO log VALUES(?,?,?,?,?,?)',
                        (source, target, operator, msg, msg_type, time()))
        self.db.commit()

    def verify_db(self):
        # FIXME: there has to be a better way to do this.
        """ Verifies that the database is going to be OK
        """
        #define needed tables and the statements used to create them
        tables_needed = {
            'log': 'CREATE TABLE log(source TEXT, target TEXT, operator INTEGER, msg TEXT, type TEXT, time INTEGER)',
        }
        #Make sure the tables are all OK
        #print ("Verifying DB");
        for tbl in tables_needed.keys():
            #print ("Checking table", tbl, end="...")
            current_tbl = self.db.execute('SELECT sql FROM sqlite_master WHERE name=?', (tbl,)).fetchone()
            if current_tbl is None:
                #print("Not extant, creating...", end="")
                self.db.execute(tables_needed[tbl])
            elif current_tbl[0] != tables_needed[tbl]:
                #Here we do some ugly text transformation hacks to see if we can get the two tablespecs to line up.
                hack_sql = lambda x: x.replace(' ', '').replace('\n', '').replace(';', '')
                if hack_sql(current_tbl[0]) != hack_sql(tables_needed[tbl]):
                    print("Not OK!")
                    print("hacked up sql strings:\n Wanted:")
                    print(hack_sql(tables_needed))
                    print("recieved")
                    print(hack_sql(current_tbl[0]))
                    print("The structure of table ", tbl, " doesn't equal what we expect!")
                    print("We Want:")
                    print(tables_needed[tbl])
                    print("but got:")
                    print(current_tbl[0])
                    print("Please execute an ALTER TABLE ", tbl, " query so that everything lines up!")
                    raise Exception("Invalid DB")
            #print(" OK")
        #print ("DB verified")
