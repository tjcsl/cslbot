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

import random


@Command(['compare', 'comparatron'])
def cmd(send, msg, args):
    """Compares something. Uncensored version at http://theycallmezeal.fwilson.me/stuffs/comparatron
    Syntax: !compare (thing)"""

    comparisons = ["nastier", "whiter", "dumber", "pastier", "crustier", "uglier", "stinkier", "more disgusting", "blacker", "crappier"]
    superlatives = ["nastiest", "whitest", "dumbest", "pastiest", "crustiest", "ugliest", "stinkiest", "most disgusting", "blackest", "crappiest"]
    people = ["Maya Angelou", "me", "yo momma", "Hillary Clinton", "Thor", "my grandmomma", "you", "the Reverend Martin Luther King, Jr", "the Pope", "Danny Devito", "Sarah Palin", "Peter Foley"]
    posessivepeople = ["Maya Angelou's", "my", "yo momma's", "Hillary Clinton's", "Thor's", "my grandmomma's", "your", "the Reverend Martin Luther King, Jr.'s", "the Pope's", "Danny Devito's", "Sarah Palin's", "Peter Foley's"]
    things = ["you-know-where", "nads", "snatch", "hole",  "legs", "butt", "body", "torso", "entire extended family", "stupid dumbass face"]

    mode = random.randint(0, 2)
    sentence = None

    if not msg:
        users = list(args['handler'].channels[args['target']].users()) if args['target'] != 'private' else ['you']
        msg = choice(users)

    if mode == 0:
        sentence = msg + " is " + random.choice(comparisons) + " than " + random.choice(posessivepeople) + " " + random.choice(things) + "."
    elif mode == 1:
        sentence = msg + " is " + random.choice(comparisons) + " than " + random.choice(people) + "."
    elif mode == 2:
        sentence = msg + " is the " + random.choice(superlatives) + " damn thing."

    send(sentence)