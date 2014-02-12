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

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from time import time
from atexit import register
from .orm import setup_db


def get_session(config):
    #FIXME: add support for sqlite connection string
    engine = create_engine('postgresql://ircbot:%s@localhost/%s' % (config['auth']['dbpass'], config['core']['dbname']))
    return Session(bind=engine)


class Sql():

    def __init__(self, config):
        """ Set everything up"""
        self.session = get_session(config)
        setup_db(self.session)
        register(self.shutdown)

    def log(self, source, target, flags, msg, msg_type):
        """ Logs a message to the database

        | source: The source of the message.
        | target: The target of the message.
        | flags: Is the user a operator or voiced?
        | msg: The text of the message.
        | msg: The type of message.
        | time: The current time (Unix Epoch).
        """
        db = self.get()
        db.execute('INSERT INTO log VALUES(%s,%s,%s,%s,%s,%s)',
                   (source, target, flags, msg, msg_type, time()))
        db.commit()

    def get(self):
        #FIXME: don't use raw sql.
        return self.session.connection()

    def shutdown(self):
        self.session.close()
