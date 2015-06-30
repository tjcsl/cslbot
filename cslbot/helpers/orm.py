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

from sqlalchemy import Column, Float, Integer, ForeignKey, Unicode, UnicodeText
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
    source = Column(UnicodeText)
    target = Column(Unicode(length=512), index=True)
    flags = Column(Integer)
    msg = Column(UnicodeText)
    type = Column(UnicodeText)
    time = Column(Float)


class Quotes(Base):
    quote = Column(UnicodeText)
    nick = Column(UnicodeText)
    submitter = Column(UnicodeText)
    approved = Column(Integer, default=0)


class Polls(Base):
    question = Column(UnicodeText)
    active = Column(Integer, default=1)
    deleted = Column(Integer, default=0)
    accepted = Column(Integer, default=0)
    submitter = Column(UnicodeText)


class Poll_responses(Base):
    response = Column(UnicodeText)
    voter = Column(UnicodeText)
    pid = Column(Integer, ForeignKey("polls.id"))


class Weather_prefs(Base):
    nick = Column(Unicode(length=20), unique=True)
    location = Column(UnicodeText)


class Scores(Base):
    nick = Column(Unicode(length=20), unique=True)
    score = Column(Integer)


class Commands(Base):
    nick = Column(UnicodeText)
    command = Column(UnicodeText)
    channel = Column(UnicodeText)


class Stopwatches(Base):
    active = Column(Integer, default=1)
    time = Column(Integer)
    elapsed = Column(Float, default=0)


class Urls(Base):
    url = Column(UnicodeText)
    title = Column(UnicodeText)
    nick = Column(UnicodeText)
    time = Column(Float)


class Issues(Base):
    title = Column(UnicodeText)
    source = Column(UnicodeText)
    description = Column(UnicodeText)
    accepted = Column(Integer, default=0)


class Notes(Base):
    note = Column(UnicodeText)
    submitter = Column(UnicodeText)
    nick = Column(UnicodeText)
    time = Column(Float)
    pending = Column(Integer, default=1)


class Babble(Base):
    __table_args__ = {'mysql_row_format': 'dynamic'}
    key = Column(Unicode(length=512), index=True)
    source = Column(UnicodeText)
    target = Column(UnicodeText)
    word = Column(UnicodeText)
    freq = Column(Integer)


class Babble_last(Base):
    last = Column(Integer)


class Babble_count(Base):
    type = Column(UnicodeText)
    key = Column(UnicodeText)
    count = Column(Integer)


class Ignore(Base):
    nick = Column(UnicodeText)
    expire = Column(Float)


class Tumblrs(Base):
    post = Column(UnicodeText)
    blogname = Column(UnicodeText)
    submitter = Column(UnicodeText)
    accepted = Column(Integer, default=0)
