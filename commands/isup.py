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

from requests import get
from helpers.command import Command


@Command('isup', ['nick'])
def cmd(send, msg, args):
    """Checks if a website is up.
    Syntax: {command} <website>
    """
    if not msg:
        send("What are you trying to get to?")
        return
    nick = args['nick']
    isup = get("http://isup.me/%s" % msg).text
    if "looks down from here" in isup:
        send("%s \x034is down\x03" % (msg))
    elif "like a site on the interwho" in isup:
        send("\x034%s is not a valid url\x03" % (msg))
    else:
        send("%s \x033is up\x03" % (msg))
