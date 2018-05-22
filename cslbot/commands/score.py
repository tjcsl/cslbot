# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from sqlalchemy import func

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Scores


@Command(["score", "points"], ["config", "db", "botnick"])
def cmd(send, msg, args):
    """Gets scores.

    Syntax: {command} <--high|--low|nick>

    """
    if not args["config"]["feature"].getboolean("hooks"):
        send(
            "Hooks are disabled, and this command depends on hooks. Please contact the bot admin(s)."
        )
        return
    session = args["db"]
    parser = arguments.ArgParser(args["config"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--high", action="store_true")
    group.add_argument("--low", action="store_true")
    group.add_argument("nick", nargs="?", action=arguments.NickParser)
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.high:
        data = session.query(Scores).order_by(Scores.score.desc()).limit(3).all()
        send("High Scores:")
        for x in data:
            send("%s: %s" % (x.nick, x.score))
    elif cmdargs.low:
        data = session.query(Scores).order_by(Scores.score).limit(3).all()
        send("Low Scores:")
        for x in data:
            send("%s: %s" % (x.nick, x.score))
    elif cmdargs.nick:
        name = cmdargs.nick.lower()
        if name == "c":
            send("We all know you love C better than anything else, so why rub it in?")
            return
        score = session.query(Scores).filter(Scores.nick == name).scalar()
        if score is not None:
            plural = "" if abs(score.score) == 1 else "s"
            if name == args["botnick"].lower():
                emote = ":)" if score.score > 0 else ":(" if score.score < 0 else ":|"
                output = "has %s point%s! %s" % (score.score, plural, emote)
                send(output, "action")
            else:
                send("%s has %i point%s!" % (name, score.score, plural))
        else:
            send("Nobody cares about %s" % name)
    else:
        if session.query(Scores).count() == 0:
            send("Nobody cares about anything =(")
        else:
            query = session.query(Scores).order_by(func.random()).first()
            plural = "" if abs(query.score) == 1 else "s"
            send("%s has %i point%s!" % (query.nick, query.score, plural))
