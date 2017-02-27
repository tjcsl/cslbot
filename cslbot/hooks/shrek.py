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

import random

from ..helpers.hook import Hook

from pkg_resources import Requirement, resource_string


def get_list():
    return resource_string(Requirement.parse('CslBot'), 'cslbot/static/allstar.txt').decode().splitlines()


@Hook('shrek', 'pubmsg', ['nick'])
def handle(send, msg, args):
    if random.random() > 0.001:
        return
    send('{}: {}'.format(args['nick'], random.choice(get_list())))
