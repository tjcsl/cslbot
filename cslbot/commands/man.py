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

from lxml.html import fromstring

from requests import get

from ..helpers import arguments
from ..helpers.command import Command


@Command('man', ['config'])
def cmd(send, msg, args):
    """Gets a man page.

    Syntax: {command} [section] <command>

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('section', nargs='?')
    parser.add_argument('command')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.section:
        html = get('http://linux.die.net/man/%s/%s' % (cmdargs.section, cmdargs.command))
        short = fromstring(html.text).find('.//meta[@name="description"]')
        if short is not None:
            short = short.get('content')
            send("%s -- http://linux.die.net/man/%s/%s" % (short, cmdargs.section, cmdargs.command))
        else:
            send("No manual entry for %s in section %s" % (cmdargs.command, cmdargs.section))
    else:
        for section in range(0, 8):
            html = get('http://linux.die.net/man/%d/%s' % (section, cmdargs.command))
            if html.status_code == 200:
                short = fromstring(html.text).find('.//meta[@name="description"]')
                if short is not None:
                    short = short.get('content')
                    send("%s -- http://linux.die.net/man/%d/%s" % (short, section, cmdargs.command))
                    return
        send("No manual entry for %s" % cmdargs.command)
