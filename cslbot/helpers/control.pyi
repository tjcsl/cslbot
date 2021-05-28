from typing import Callable

from . import handler

def handle_ctrlchan(handler: handler.BotHandler, msg: str, nick: str, send: Callable[[str], None]) -> None:
    ...
