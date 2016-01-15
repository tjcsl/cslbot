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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import configparser
import logging
from os.path import dirname, exists, join
from sys import path

from alembic import context
from sqlalchemy import create_engine

# Make this work from git.
if exists(join(dirname(__file__), '../../.git')):
    path.insert(0, join(dirname(__file__), '../..'))

from cslbot.helpers import orm  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# This line sets up loggers basically.
logging.basicConfig(level=logging.INFO)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = orm.Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    botconfig = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config_path = config.get_main_option('bot_config_path', join(dirname(__file__), '../..'))
    with open(join(config_path, 'config.cfg')) as f:
        botconfig.read_file(f)
    url = botconfig['db']['engine']

    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    botconfig = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config_path = config.get_main_option('bot_config_path', join(dirname(__file__), '../..'))
    with open(join(config_path, 'config.cfg')) as f:
        botconfig.read_file(f)
    url = botconfig['db']['engine']

    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
