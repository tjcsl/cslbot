# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
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
from threading import current_thread
from time import time
from os.path import dirname


class Sql():

    def __init__(self):
        """ Set everything up

        | dbfile is the filename of the database
        | connection_pool is a dictionary of threadid->dbconnection.
        """
        self.dbfile = dirname(__file__) + '/../db.sqlite'
        self.connection_pool = {}
        self.setup_db()

    def log(self, source, target, flags, msg, msg_type):
        """ Logs a message to the database

        | source: The source of the message.
        | target: The target of the message.
        | flags: Is the user a operator or voiced?
        | msg: The text of the message.
        | msg: The type of message.
        | time: The current time (Unix Epoch).
        """
        db = self.get_db_for_current_thread()
        db.execute('INSERT INTO log VALUES(?,?,?,?,?,?)',
                   (source, target, flags, msg, msg_type, time()))
        db.commit()

    def get_db_for_current_thread(self):
        """ Gets a database connection unique to the current thread
        """
        tid = current_thread().ident
        if tid in self.connection_pool.keys():
            return self.connection_pool[tid]
        else:
            dbconn = sqlite3.connect(self.dbfile)
            dbconn.row_factory = sqlite3.Row
            self.connection_pool[tid] = dbconn
            return dbconn

    def clean_connection_pool(self):
        """ Cleans out the connection pool.
        """
        for conn in self.connection_pool.values():
            conn.commit()
            conn.close()
        self.connection_pool.clear()

    def get(self):
        return self.get_db_for_current_thread()

    def setup_db(self):
        """ Sets up the database.
        """
        db = self.get_db_for_current_thread()
        db.execute('CREATE TABLE IF NOT EXISTS log(source TEXT, target TEXT, operator INTEGER, msg TEXT, type TEXT, time INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS quotes(quote TEXT, nick TEXT, submitter TEXT, approved INTEGER DEFAULT 0,\
                   id INTEGER PRIMARY KEY AUTOINCREMENT)')
        db.execute('CREATE TABLE IF NOT EXISTS polls(question TEXT, active INTEGER DEFAULT 1, deleted INTEGER DEFAULT 0,\
                   accepted INTEGER DEFAULT 0, submitter TEXT, pid INTEGER PRIMARY KEY AUTOINCREMENT)')
        db.execute('CREATE TABLE IF NOT EXISTS poll_responses(pid INTEGER, response TEXT, voter TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS weather_prefs(nick TEXT UNIQUE, location TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS scores(nick TEXT UNIQUE, score INTEGER, id INTEGER PRIMARY KEY AUTOINCREMENT)')
        db.execute('CREATE TABLE IF NOT EXISTS commands(nick TEXT, command TEXT, channel TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS stopwatches (id INTEGER PRIMARY KEY AUTOINCREMENT, active INTEGER DEFAULT 1,\
                   time INTEGER, elapsed INTEGER DEFAULT 0)')
        db.execute('CREATE TABLE IF NOT EXISTS urls (url TEXT, title TEXT, time INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS issues (title TEXT, source TEXT, accepted INTEGER DEFAULT 0,\
                   id INTEGER PRIMARY KEY AUTOINCREMENT)')
