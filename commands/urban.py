# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from urllib.parse import quote
from urllib.request import urlopen
from helpers.command import Command
import json


@Command('urban')
def cmd(send, msg, args):
    """Gets a definition from urban dictionary.
    Syntax: !urban <term>
    """
    if not msg:
        send("Lookup what?")
        return
    msgSplit = msg.split(' ')
    definitionNum = None
    if msgSplit[-1][0] == '#':
        try:
            definitionNum = int(msgSplit[-1][1:])
        except:
            pass
    if not msg:
        return
    data = json.loads(urlopen('http://api.urbandictionary.com/v0/define?term=%s' % (quote(toStr(msgSplit[:(len(msgSplit))]) if not definitionNum else toStr(msgSplit[:(len(msgSplit) - 1)])))).read().decode())
    try:
        if definitionNum:
            definition = data['list'][definitionNum - 1]['definition'].replace('\n', ' ')
        else:
            definition = data['list'][0]['definition'].replace('\n', ' ')
        send(definition.replace('shit', '$#!+').replace('fuck', 'fsck'))
    except IndexError:
        send("UrbanDictionary doesn't have a answer for you.")


def toStr(arrToSplit):
    endStr = arrToSplit[0]
    for i in arrToSplit[1:]:
        endStr += ' '
        endStr += i
    return endStr
