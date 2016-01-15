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

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.textutils import gen_translate


@Command(['translate', 'trans'], ['config'])
def cmd(send, msg, args):
    """Translate something.
    Syntax: {command} [--lang <language code>] <text>
    See https://msdn.microsoft.com/en-us/library/hh456380.aspx for a list of valid language codes
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--lang', '--language', default='en')
    parser.add_argument('msg', nargs='+')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    send(gen_translate(' '.join(cmdargs.msg), outputlang=cmdargs.lang))
