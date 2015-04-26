from alembic import context
import configparser
import sys
from sqlalchemy import create_engine
import logging
from os.path import dirname, join
# Fix path to import from helpers
sys.path.insert(0, join(dirname(__file__), '..'))
from helpers.orm import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# This line sets up loggers basically.
logging.basicConfig(level=logging.INFO)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(join(dirname(__file__), '../config.cfg')) as f:
        config.read_file(f)
    url = config['db']['engine']

    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(join(dirname(__file__), '../config.cfg')) as f:
        config.read_file(f)
    url = config['db']['engine']

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
