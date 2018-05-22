# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from ..helpers import arguments
from ..helpers.command import Command


def gen_stock(msg):
    quote = get("http://dev.markitondemand.com/Api/v2/Quote/json", params={"symbol": msg}).json()
    if "Message" in quote.keys():
        return quote["Message"]
    else:
        changepercent = "%.3f%%" % quote["ChangePercent"]
        if quote["ChangePercent"] >= 0:
            changepercent = "+" + changepercent
        return "%s (%s) as of %s: %s %s High: %s Low: %s" % (
            quote["Name"],
            msg,
            quote["Timestamp"],
            quote["LastPrice"],
            changepercent,
            quote["High"],
            quote["Low"],
        )


def random_stock():
    html = get("http://www.openicon.com/rsp/rsp_n100.php").text
    return re.search(r"\((.*)\)", html).group(1)


@Command("stock", ["config"])
def cmd(send, msg, args):
    """Gets a stock quote.

    Syntax: {command} [symbol]
    Powered by markit on demand (http://dev.markitondemand.com)

    """
    parser = arguments.ArgParser(args["config"])
    parser.add_argument("stock", nargs="?", default=random_stock())
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    send(gen_stock(cmdargs.stock))
