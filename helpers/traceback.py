# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import traceback
from os.path import basename


def handle_traceback(ex, c, target):
    traceback.print_exc()
    trace = traceback.extract_tb(ex.__traceback__)[-1]
    trace = [basename(trace[0]), trace[1]]
    name = type(ex).__name__
    output = str(ex).replace('\n', ' ')
    c.privmsg(target, '%s in %s on line %s: %s' % (name, trace[0], trace[1], output))
