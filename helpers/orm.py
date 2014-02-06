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

from sqlalchemy import MetaData, Table, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

Base = declarative_base(cls=Base)


class Log(Base):
    id = Column(Integer, primary_key=True)


def setup_db(session):
    """ Sets up the database.
    """

    #Base.metadata.create_all(session.connection())
    metadata = MetaData()
    Table('log', metadata,
          Column('source', String),
          Column('target', String),
          Column('operator', Integer),
          Column('msg', String),
          Column('type', String),
          Column('time', Float))
    Table('quotes', metadata,
          Column('quote', String),
          Column('nick', String),
          Column('submitter', String),
          Column('approved', Integer, default=0),
          Column('id', Integer, primary_key=True))
    Table('polls', metadata,
          Column('question', String),
          Column('active', Integer, default=1),
          Column('deleted', Integer, default=0),
          Column('accepted', Integer, default=0),
          Column('submitter', String),
          Column('pid', Integer, primary_key=True))
    Table('poll_responses', metadata,
          Column('pid', Integer),
          Column('response', String),
          Column('voter', String))
    Table('weather_prefs', metadata,
          Column('nick', String, unique=True),
          Column('location', String))
    Table('scores', metadata,
          Column('nick', String, unique=True),
          Column('score', Integer),
          Column('id', Integer, primary_key=True))
    Table('commands', metadata,
          Column('nick', String),
          Column('command', String),
          Column('channel', String))
    Table('stopwatches', metadata,
          Column('id', Integer, primary_key=True),
          Column('active', Integer, default=1),
          Column('time', Integer),
          Column('elapsed', Float, default=0))
    Table('urls', metadata,
          Column('url', String),
          Column('title', String),
          Column('nick', String),
          Column('time', Float))
    Table('issues', metadata,
          Column('title', String),
          Column('source', String),
          Column('accepted', Integer, default=0),
          Column('id', Integer, primary_key=True))
    Table('notes', metadata,
          Column('note', String),
          Column('submitter', String),
          Column('nick', String),
          Column('time', Float),
          Column('pending', Integer, default=1),
          Column('id', Integer, primary_key=True))
    Table('nicks', metadata,
          Column('old', String),
          Column('new', String),
          Column('time', Float))
    metadata.create_all(session.connection())
