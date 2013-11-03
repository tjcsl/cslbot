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

import requests
from helpers.command import Command
import html#.parser

@Command('fmltest', ['config'])
def cmd(send, msg, args):
    """Gets a random FML post.
    Syntax: !fml
    """
    link = "http://api.fmylife.com/view/random/nosex/?key=%s&language=en" % args['config']['api']['fmlapikey']
    req = requests.get("http://api.fmylife.com/view/random/nosex/?key=%s&language=en" % args['config']['api']['fmlapikey'])
    send(html.parser.HTMLParser().unescape(req.text.split("<text>")[1].split("</text>")[0]))
