# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from helpers.command import Command


# prevent people from !8balling repeatedly to get the answer they want.
@Command('8ball', ['nick', 'handler'], limit=1)
def cmd(send, msg, args):
    """Asks the Magic 8-Ball a question.
    Syntax: !8ball <question>
    """
    if not msg:
        send("What is your question?")
        # let people !8ball again if they screw up and forget the part where you ask a question.
        args['handler'].abuselist[args['nick']]['8ball'].pop()
        return
    answers = {"It is certain": "yes", "It is decidedly so": "yes", "Without a doubt": "yes", "Yes, definitely": "yes", "You may rely on it": "yes", "As I see it, yes": "yes",
               "Most likely": "yes", "Outlook good": "yes", "Yes": "yes", "Signs point to yes": "yes",
               "Reply hazy, try again": "maybe", "Ask again later": "maybe", "Better not tell you now": "maybe", "Cannot predict now": "maybe", "Concentrate and ask again": "maybe",
               "Don't count on it": "no", "My reply is no": "no", "My sources say no": "no", "Outlook not so good": "no", "Very doubtful": "no"}
    answer = choice(list(answers.keys()))
    # let people !8ball again if they got a ambiguous answer.
    if answers[answer] == 'maybe':
        args['handler'].abuselist[args['nick']]['8ball'].pop()
    send('says... %s' % answer, 'action')
