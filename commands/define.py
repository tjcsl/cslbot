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
    word = cmdargs.word if cmdargs.word is not None else textutils.gen_word()
    req = get('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s' % word, params={'key': args['config']['api']['dictionaryapikey']})
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

    if cmdargs.entry >= len(defs):
        if cmdargs.word:
            send("Definition not found")
        else:
            send("%s: Definition not found" % word)
    else:
        if cmdargs.word:
            send(defs[cmdargs.entry])
        else:
            send("%s: %s" % (word, defs[cmdargs.entry]))
