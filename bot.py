#!/usr/bin/env python3
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

import warnings
from os.path import abspath, dirname
from sys import path

warnings.simplefilter('default')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='alembic.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='nltk')
warnings.filterwarnings('ignore', category=PendingDeprecationWarning, module='nltk')

path.insert(0, dirname(abspath(__file__)))

from cslbot.helpers import core  # noqa

if __name__ == '__main__':
    core.init(dirname(abspath(__file__)))
