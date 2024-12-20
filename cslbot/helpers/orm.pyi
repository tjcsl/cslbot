from typing import Any

class Base:
    id: Any = ...

    def __init__(self, *args, **kwargs) -> None:
        ...

    def __tablename__(self):
        ...


def setup_db(session: Any, botconfig: Any, confdir: Any) -> None:
    ...


class Log(Base):
    source: Any = ...
    target: Any = ...
    flags: Any = ...
    msg: Any = ...
    type: Any = ...
    time: Any = ...


class Quotes(Base):
    quote: Any = ...
    nick: Any = ...
    submitter: Any = ...
    accepted: Any = ...


class Polls(Base):
    question: Any = ...
    active: Any = ...
    deleted: Any = ...
    accepted: Any = ...
    submitter: Any = ...


class Poll_responses(Base):
    response: Any = ...
    voter: Any = ...
    pid: Any = ...


class Weather_prefs(Base):
    nick: Any = ...
    location: Any = ...


class Scores(Base):
    nick: Any = ...
    score: Any = ...


class Commands(Base):
    nick: Any = ...
    command: Any = ...
    channel: Any = ...


class Stopwatches(Base):
    active: Any = ...
    time: Any = ...
    elapsed: Any = ...


class Urls(Base):
    url: Any = ...
    title: Any = ...
    nick: Any = ...
    time: Any = ...


class Issues(Base):
    title: Any = ...
    source: Any = ...
    description: Any = ...
    accepted: Any = ...


class Notes(Base):
    note: Any = ...
    submitter: Any = ...
    nick: Any = ...
    time: Any = ...
    pending: Any = ...


class Babble(Base):
    __table_args__: Any = ...
    key: Any = ...
    source: Any = ...
    target: Any = ...
    word: Any = ...
    freq: Any = ...


class Babble2(Base):
    __table_args__: Any = ...
    key: Any = ...
    source: Any = ...
    target: Any = ...
    word: Any = ...
    freq: Any = ...


class Babble_last(Base):
    last: Any = ...


class Babble_count(Base):
    type: Any = ...
    length: Any = ...
    key: Any = ...
    count: Any = ...


class Ignore(Base):
    nick: Any = ...
    expire: Any = ...


class Tumblrs(Base):
    post: Any = ...
    blogname: Any = ...
    submitter: Any = ...
    accepted: Any = ...


class UrbanBlacklist(Base):
    word: Any = ...


class Permissions(Base):
    nick: Any = ...
    role: Any = ...
    registered: Any = ...
    time: Any = ...
