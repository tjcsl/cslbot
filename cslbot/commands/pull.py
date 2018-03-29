# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import logging
import subprocess
from os.path import exists, join

from ..helpers.command import Command
from ..helpers.misc import do_pull


@Command('pull', ['config', 'handler'], role="owner")
def cmd(send, _, args):
    """Pull changes.

    Syntax: {command} <branch>

    """
    try:
        if exists(join(args['handler'].confdir, '.git')):
            send(do_pull(srcdir=args['handler'].confdir))
        else:
            send(do_pull(repo=args['config']['api']['githubrepo']))
    except subprocess.CalledProcessError as ex:
        for line in ex.output.decode().strip().splitlines():
            logging.error(line)
        raise ex
