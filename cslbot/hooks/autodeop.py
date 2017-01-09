# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from ..helpers.hook import Hook


@Hook('autodeop', ['pubmsg', 'action', 'mode'], ['config', 'target', 'type', 'handler'])
def handle(_, msg, args):
    if 'autodeop' not in args['config']['core']:
        return

    to_deop = [x.strip() for x in args['config']['core']['autodeop'].split(',')]

    if args['type'] == 'mode':
        for nick in to_deop:
            if re.match(r'^\+[^ ]*o.+%s.*$' % nick, msg):
                args['handler'].connection.mode(args['target'], '-o %s' % nick)
    else:
        with args['handler'].data_lock:
            for nick in to_deop:
                if nick in args['handler'].opers[args['target']]:
                    args['handler'].connection.mode(args['target'], '-o %s' % nick)
