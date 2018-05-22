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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import logging
import traceback
from os.path import basename

from irc import client

from . import misc


def output_traceback(ex):
    """Returns a tuple of a prettyprinted error message and string representation of the error."""
    # Dump full traceback to console.
    output = "".join(traceback.format_exc()).strip()
    for line in output.split("\n"):
        logging.error(line)
    trace_obj = traceback.extract_tb(ex.__traceback__)[-1]
    trace = [basename(trace_obj[0]), trace_obj[1]]
    name = type(ex).__name__
    output = str(ex).replace("\n", " ")
    msg = "%s in %s on line %s: %s" % (name, trace[0], trace[1], output)
    return (msg, output)


def handle_traceback(ex, c, target, config, source="the bot"):
    msg, output = output_traceback(ex)
    name = type(ex).__name__
    ctrlchan = config["core"]["ctrlchan"]
    prettyerrors = config["feature"].getboolean("prettyerrors")
    # If we've disconnected, there isn't much point sending errors to the network.
    if isinstance(ex, client.ServerNotConnectedError):

        def send(_, msg):
            logging.error(msg)

    else:
        send = c.privmsg
    errtarget = ctrlchan if prettyerrors else target
    if prettyerrors and target != ctrlchan:
        if name == "CommandFailedException":
            send(target, "%s -- %s" % (source, output))
        else:
            send(target, "%s occured in %s. See the control channel for details." % (name, source))
    msg = "Error in channel %s -- %s -- %s" % (target, source, msg)
    # Handle over-long exceptions.
    max_len = misc.get_max_length(errtarget, "privmsg")
    msg = misc.truncate_msg(msg, max_len)
    send(errtarget, msg)
