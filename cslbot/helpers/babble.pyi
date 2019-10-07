from sqlalchemy import orm
from typing import Optional


def get_messages(cursor, cmdchar, ctrlchan, speaker, newer_than_id):
    ...


def clean_msg(msg):
    ...


def get_markov(cursor, length, node, initial_run):
    ...


def update_count(cursor, length, source, target):
    ...


def generate_markov(cursor, length, messages, initial_run):
    ...


def build_rows(cursor, length, markov, initial_run):
    ...


def postgres_hack(cursor, length, data):
    ...


def delete_tables(cursor):
    ...


def build_markov(cursor: orm.Session, cmdchar: str, ctrlchan: str, speaker: Optional[str] = None, initial_run: bool = False,
                 debug: bool = False) -> None:
    ...


def update_markov(cursor, config):
    ...
