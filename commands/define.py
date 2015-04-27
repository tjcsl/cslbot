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

import re
from requests import get
from lxml import etree
from helpers import arguments, textutils
from helpers.command import Command


def strip_colon(msg):
    return re.sub('^:|:$', '', msg.strip()).strip()


def get_def(entry, word, key):
    req = get('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s' % word, params={'key': key})
    xml = etree.fromstring(req.content)
    defs = []
    for defn in xml.findall('./entry/def/dt'):
        if defn.text is not None:
            elems = [strip_colon(defn.text)]
        else:
            elems = []
        for elem in defn.xpath('*[not(self::ca|self::dx|self::vi|self::un|self::sx)]'):
            elems.append(strip_colon(elem.text))
        def_str = ' '.join(elems)
        if def_str:
            defs.append(def_str)
    if entry >= len(defs):
        suggestion = xml.find('./suggestion')
        if suggestion is None:
            return None, None
        defn, _ = get_def(0, suggestion.text, key)
        if defn is None:
            return None, None
        else:
            return defn, suggestion.text
    else:
        return defs[entry], None


@Command('define', ['config'])
def cmd(send, msg, args):
    """Gets the definition of a word.
    Syntax: {command} [--entry <num>] <word>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--entry', type=int, default=0, nargs='?')
    parser.add_argument('word', nargs='?')

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    key = args['config']['api']['dictionaryapikey']
    if cmdargs.word is None:
        for _ in range(5):
            word = textutils.gen_word()
            defn, suggested_word = get_def(0, textutils.gen_word(), key)
            word = suggested_word if suggested_word is not None else word
            if defn is not None:
                send("%s: %s" % (word, defn))
                return
        send("%s: Definition not found" % word)
        return
    defn, suggested_word = get_def(cmdargs.entry, cmdargs.word, key)
    if defn is None:
        send("Definition not found")
    elif suggested_word is None:
        send(defn)
    else:
        send("%s: %s" % (suggested_word, defn))
