# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi,
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
import sys
from os.path import basename


def get_traceback(ex):
    # Dump full traceback to console.
    traceback.print_exc()
    # Force traceback to be flushed
    sys.stderr.flush()
    trace = traceback.extract_tb(ex.__traceback__)[-1]
    trace = [basename(trace[0]), trace[1]]
    name = type(ex).__name__
    output = str(ex).replace('\n', ' ')
    msg = "%s in %s on line %s: %s" % (name, trace[0], trace[1], output)
    return (msg, output)


def handle_traceback(ex, c, target, config, source="the bot"):
    msg, output = get_traceback(ex)
    name = type(ex).__name__
    ctrlchan = config['core']['ctrlchan']
    prettyerrors = config['feature'].getboolean('prettyerrors')
    errtarget = ctrlchan if prettyerrors else target
    if prettyerrors and target != ctrlchan:
        if name == 'CommandFailedException':
            c.privmsg(target, "%s -- %s" % (source, output))
        else:
            c.privmsg(target, "%s occured in %s. See the control channel for details." % (name, source))
    c.privmsg(errtarget, 'Error in channel %s -- %s -- %s' % (target, source, msg))
