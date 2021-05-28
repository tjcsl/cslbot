from irc import bot

from .handler import BotHandler

class IrcBot(bot.SingleServerIRCBot):

    def __init__(self, confdir: str) -> None:
        ...

    handler = ...  # type: BotHandler


def init(confdir: str) -> None:
    ...
