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

import subprocess
from helpers.orm import Scores
from helpers.command import Command


def get_scores(cursor):
    rows = cursor.query(Scores).all()
    return {row.nick: row.score for row in rows}


@Command(['bc', 'math'], ['db'])
def cmd(send, msg, args):
    """Evaluates mathmatical expressions.
    Syntax: {command} <expression>
    """
    if not msg:
        send("Calculate what?")
        return
    cursor = args['db']
    scores = get_scores(cursor)
    for word in msg.split():
        if word in scores:
            msg = msg.replace(word, str(scores[word]))
    msg += '\n'
    proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = proc.communicate(msg.encode(), timeout=5)[0].decode().splitlines()
    except subprocess.TimeoutExpired:
        proc.terminate()
        send("Execution took too long, you might have better luck with WolframAlpha.")
        return
    if len(output) > 3:
        send("Your output is too long, have you tried mental math?")
    else:
        for line in output:
            send(line)
