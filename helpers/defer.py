# -*- coding: utf-8 -*-
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi,
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

from helpers.workers import add_thread, get_thread
from threading import Thread, current_thread, get_ident


def _defer(t, function, args):
    add_thread(current_thread())
    if not get_thread(get_ident())[1].wait(int(t)):
        function(*args)


def defer(t, function, *args):
    """
    Defers an function with args for t seconds. Returns a Thread representing
    the function to be deferred (i.e. it can be killed to cancel defer).
    """
    Thread(target=_defer, args=(t, function, args)).start()
