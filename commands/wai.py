from helpers.command import Command
from random import choice


@Command('wai', [])
def cmd(send, msg, args):
    """Gives a reason for something.
    Syntax: !wai
    """
    a = ["primary", "secondary", "tertiary", "hydraulic", "compressed",
         "required", "pseudo", "intangible"]
    b = ["compressor", "engine", "lift", "elevator", "irc bot", "stabilizer",
         "computer", "ahamilto", "csl", "4506", "router", "switch", "thingy"]
    c = ["broke", "exploded", "corrupted", "melted", "froze", "died", "reset",
         "was seen by the godofskies", "burned", "corroded",
         "was accidentallied"]
    send(" ".join((choice(a), choice(b), choice(c))))
