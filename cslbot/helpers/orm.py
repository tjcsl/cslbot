# -*- coding: utf-8 -*-
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

from alembic import command, config

from pkg_resources import Requirement, resource_filename

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Unicode, UnicodeText
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


def setup_db(session, botconfig, confdir):
    """ Sets up the database.
    """
    Base.metadata.create_all(session.connection())
    # If we're creating a fresh db, we don't need to worry about migrations.
    if not session.get_bind().has_table('alembic_version'):
        conf_obj = config.Config()
        script_location = resource_filename(Requirement.parse('CslBot'), botconfig['alembic']['script_location'])
        conf_obj.set_main_option('script_location', script_location)
        conf_obj.set_main_option('bot_config_path', confdir)
        command.stamp(conf_obj, 'head')


class Log(Base):
    source = Column(UnicodeText)
    target = Column(Unicode(length=512), index=True)
    flags = Column(Integer)
    msg = Column(UnicodeText)
    type = Column(UnicodeText)
    time = Column(DateTime)


class Quotes(Base):
    quote = Column(UnicodeText)
    nick = Column(UnicodeText)
    submitter = Column(UnicodeText)
    accepted = Column(Integer, default=0)


class Polls(Base):
    question = Column(UnicodeText)
    active = Column(Integer, default=1)
    deleted = Column(Integer, default=0)
    accepted = Column(Integer, default=0)
    submitter = Column(UnicodeText)


class Poll_responses(Base):  # noqa
    response = Column(UnicodeText)
    voter = Column(UnicodeText)
    pid = Column(Integer, ForeignKey("polls.id"))


class Weather_prefs(Base):  # noqa
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
    time = Column(DateTime)
    elapsed = Column(DateTime)


class Urls(Base):
    url = Column(UnicodeText)
    title = Column(UnicodeText)
    nick = Column(UnicodeText)
    time = Column(DateTime)


class Issues(Base):
    title = Column(UnicodeText)
    source = Column(UnicodeText)
    description = Column(UnicodeText)
    accepted = Column(Integer, default=0)


class Notes(Base):
    note = Column(UnicodeText)
    submitter = Column(UnicodeText)
    nick = Column(UnicodeText)
    time = Column(DateTime)
    pending = Column(Integer, default=1)


class Babble(Base):
    __table_args__ = {'mysql_row_format': 'dynamic'}
    key = Column(Unicode(length=512), index=True)
    source = Column(UnicodeText)
    target = Column(UnicodeText)
    word = Column(UnicodeText)
    freq = Column(Integer)


class Babble2(Base):
    __table_args__ = {'mysql_row_format': 'dynamic'}
    key = Column(Unicode(length=512), index=True)
    source = Column(UnicodeText)
    target = Column(UnicodeText)
    word = Column(UnicodeText)
    freq = Column(Integer)


class Babble_last(Base):  # noqa
    last = Column(Integer)


class Babble_count(Base):  # noqa
    type = Column(UnicodeText)
    length = Column(Integer)
    key = Column(UnicodeText)
    count = Column(Integer)


class Ignore(Base):
    nick = Column(UnicodeText)
    expire = Column(DateTime)


class Tumblrs(Base):
    post = Column(UnicodeText)
    blogname = Column(UnicodeText)
    submitter = Column(UnicodeText)
    accepted = Column(Integer, default=0)


class UrbanBlacklist(Base):
    word = Column(UnicodeText)


class Permissions(Base):
    nick = Column(UnicodeText)
    role = Column(Enum("owner", "admin", name="role_enum"))
    registered = Column(Boolean, default=False)
    time = Column(DateTime)
