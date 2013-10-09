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

import json
from urllib.request import urlopen
from helpers.command import Command


def get_quote(symbol):
    url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20WHERE%20symbol%3D'" + symbol \
        + "'&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
    data = json.loads(urlopen(url).read().decode())
    return data['query']['results']['quote']


@Command('stock')
def cmd(send, msg, args):
    """Gets a stock quote.
    Syntax: !stock <symbol>
    """
    if not msg:
        send("Which Symbol?")
        return
    quote = get_quote(msg)
    if quote['Ask'] is None:
        send("Invalid Symbol.")
    else:
        send("Current: %s Change: %s 52wk: %s" % (quote['BidRealtime'], quote['ChangeinPercent'], quote['YearRange']))
