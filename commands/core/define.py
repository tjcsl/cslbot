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

from requests import get
from xml.etree import ElementTree
from helpers.command import Command


@Command('define', ['config'])
def cmd(send, msg, args):
    """Gets the definition of a word.
    Syntax: !define <word>
    """
    if not msg:
        send("Define what?")
        return
    req = get('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s' % msg, params={'key': args['config']['api']['dictionaryapikey']})
    xml = ElementTree.fromstring(req.text)
    word = xml.find('./entry/def/dt')
    if not hasattr(word, 'text') or word.text is None:
        send("Definition not found")
        return
    word = word.text.replace(' :', ', ')
    if word[-1] == ',':
        word = word[:-2]
    if word[0] == ':':
        word = word[1:]
    if not word:
        send("Definition not found")
    send(word)
