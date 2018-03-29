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

from random import choice

from ..helpers.command import Command


@Command('8ball', ['nick', 'handler'], limit=5)
def cmd(send, msg, args):
    """Asks the Magic 8-Ball a question.
    Syntax: {command} <question>
    """
    if not msg:
        send("What is your question?")
        # let people !8ball again if they screw up and forget the part where you ask a question.
        args['handler'].abuselist[args['nick']]['8ball'].pop()
        return
    answers = {
        "It is certain": "yes",
        "It is decidedly so": "yes",
        "Without a doubt": "yes",
        "Yes, definitely": "yes",
        "You may rely on it": "yes",
        "As I see it, yes": "yes",
        "Most likely": "yes",
        "Outlook good": "yes",
        "Yes": "yes",
        "Signs point to yes": "yes",
        "Reply hazy, try again": "maybe",
        "Ask again later": "maybe",
        "Better not tell you now": "maybe",
        "Cannot predict now": "maybe",
        "Concentrate and ask again": "maybe",
        "Don't count on it": "no",
        "My reply is no": "no",
        "My sources say no": "no",
        "Outlook not so good": "no",
        "Very doubtful": "no"
    }
    answer = choice(list(answers.keys()))
    send('says... %s' % answer, 'action')
