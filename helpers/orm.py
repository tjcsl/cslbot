# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


def setup_db(session):
    """ Sets up the database.
    """
    Base.metadata.create_all(session.connection())


class Log(Base):
    source = Column(String)
    target = Column(String, index=True)
    flags = Column(Integer)
    msg = Column(String)
    type = Column(String)
    time = Column(Float)


class Quotes(Base):
    quote = Column(String)
    nick = Column(String)
    submitter = Column(String)
    approved = Column(Integer, default=0)


class Polls(Base):
    question = Column(String)
    active = Column(Integer, default=1)
    deleted = Column(Integer, default=0)
    accepted = Column(Integer, default=0)
    submitter = Column(String)


class Poll_responses(Base):
    response = Column(String)
    voter = Column(String)
    pid = Column(Integer, ForeignKey("polls.id"))


class Weather_prefs(Base):
    nick = Column(String, unique=True)
    location = Column(String)


class Scores(Base):
    nick = Column(String, unique=True)
    score = Column(Integer)


class Commands(Base):
    nick = Column(String)
    command = Column(String)
    channel = Column(String)


class Stopwatches(Base):
    active = Column(Integer, default=1)
    time = Column(Integer)
    elapsed = Column(Float, default=0)


class Urls(Base):
    url = Column(String)
    title = Column(String)
    nick = Column(String)
    time = Column(Float)


class Issues(Base):
    title = Column(String)
    source = Column(String)
    desc = Column(String)
    accepted = Column(Integer, default=0)


class Notes(Base):
    note = Column(String)
    submitter = Column(String)
    nick = Column(String)
    time = Column(Float)
    pending = Column(Integer, default=1)


class Nicks(Base):
    old = Column(String)
    new = Column(String)
    time = Column(Float)


class Babble(Base):
    key = Column(String)
    source = Column(String)
    target = Column(String)
    word = Column(String)
    freq = Column(Integer)


class Babble_last(Base):
    last = Column(Integer)


class Babble_count(Base):
    type = Column(String)
    key = Column(String)
    count = Column(Integer)
