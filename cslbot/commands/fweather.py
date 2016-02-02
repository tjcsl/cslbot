# -*- coding: utf-8 -*-
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

from lxml.html import fromstring  # type: ignore

from requests import get

from ..helpers.command import Command


@Command('fweather')
def cmd(send, msg, _):
    """Gets the F***ING weather!
    Syntax: {command} <location>
    """
    req = get('http://thefuckingweather.com/April/%s' % msg)
    doc = fromstring(req.text)
    elem = doc.find('.//h1')
    if elem is None:
        send('NO FSCKING RESULTS.')
    else:
        send(elem.text)
