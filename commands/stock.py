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

import re
from requests import get
from helpers.command import Command


def get_quote(symbol):
    params = {'q': "select BidRealtime,Name,ChangeinPercent,YearRange from yahoo.finance.quotes WHERE symbol='%s'" % symbol,
              'format': 'json', 'env': 'store://datatables.org/alltableswithkeys'}
    data = get("http://query.yahooapis.com/v1/public/yql", params=params).json()
    return data['query']['results']


def gen_stock(msg):
    quote = None
    while quote is None:
        quote = get_quote(msg)
    quote = quote['quote']
    if quote['BidRealtime'] is None:
        return "Invalid Symbol."
    else:
        return "%s (%s) -- %s %s 52wk: %s" % (quote['Name'], msg, quote['BidRealtime'], quote['ChangeinPercent'], quote['YearRange'])


def random_stock():
    html = get('http://www.openicon.com/rsp/rsp_n100.php').text
    return re.search('\((.*)\)', html).group(1)


@Command('stock')
def cmd(send, msg, args):
    """Gets a stock quote.
    Syntax: !stock <symbol>
    """
    if not msg:
        msg = random_stock()
    send(gen_stock(msg))
