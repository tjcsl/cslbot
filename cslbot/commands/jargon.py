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

from random import choice

from ..helpers.command import Command

abbrev = [
    "TCP",
    "HTTP",
    "SDD",
    "RAM",
    "GB",
    "CSS",
    "SSL",
    "AGP",
    "SQL",
    "FTP",
    "PCI",
    "AI",
    "ADP",
    "RSS",
    "XML",
    "EXE",
    "COM",
    "HDD",
    "THX",
    "SMTP",
    "SMS",
    "USB",
    "PNG",
]

adj = [
    "auxiliary",
    "primary",
    "back-end",
    "digital",
    "open-source",
    "virtual",
    "cross-platform",
    "redundant",
    "online",
    "haptic",
    "multi-byte",
    "bluetooth",
    "wireless",
    "1080p",
    "neural",
    "optical",
    "solid state",
    "mobile",
]

noun = [
    "driver",
    "protocol",
    "bandwidth",
    "panel",
    "microchip",
    "program",
    "port",
    "card",
    "array",
    "interface",
    "system",
    "sensor",
    "firewall",
    "hard drive",
    "pixel",
    "alarm",
    "feed",
    "monitor",
    "application",
    "transmitter",
    "bus",
    "circuit",
    "capacitor",
    "matrix",
]

verb = [
    "back up",
    "bypass",
    "hack",
    "override",
    "compress",
    "copy",
    "navigate",
    "index",
    "connect",
    "generate",
    "quantify",
    "calculate",
    "synthesize",
    "input",
    "transmit",
    "program",
    "reboot",
    "parse",
]

ingverb = [
    "backing up",
    "bypassing",
    "hacking",
    "overriding",
    "compressing",
    "copying",
    "navigating",
    "indexing",
    "connecting",
    "generating",
    "quantifying",
    "calculating",
    "synthesizing",
    "transmitting",
    "programming",
    "parsing",
]


@Command("jargon")
def cmd(send, *_):
    """Causes the bot to generate some jargon.

    Syntax: {command}

    """
    words = [
        [verb, noun, abbrev, noun, adj, abbrev, noun],
        [verb, adj, abbrev, noun],
        [verb, abbrev, noun, verb, adj, noun],
        [verb, noun, ingverb, adj, abbrev, noun],
        [adj, abbrev, noun, verb, adj, noun],
        [abbrev, noun, verb, adj, noun, verb, abbrev, noun],
        [ingverb, noun, verb, adj, abbrev, noun],
        [verb, adj, abbrev, noun, verb, abbrev, noun],
    ]
    msgtype = [
        "If we %s the %s, we can get to the %s %s through the %s %s %s!"
        % tuple(map(choice, words[0])),
        "We need to %s the %s %s %s!" % tuple(map(choice, words[1])),
        "Try to %s the %s %s, maybe it will %s the %s %s!" % tuple(map(choice, words[2])),
        "You can't %s the %s without %s the %s %s %s!" % tuple(map(choice, words[3])),
        "Use the %s %s %s, then you can %s the %s %s!" % tuple(map(choice, words[4])),
        "The %s %s is down, %s the %s %s so we can %s the %s %s!" % tuple(map(choice, words[5])),
        "%s the %s won't do anything, we need to %s the %s %s %s!" % tuple(map(choice, words[6])),
        "I'll %s the %s %s %s, that should %s the %s %s!" % tuple(map(choice, words[7])),
    ]

    send(choice(msgtype))
