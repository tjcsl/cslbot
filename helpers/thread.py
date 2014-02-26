# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from threading import Lock
from concurrent.futures import ThreadPoolExecutor

_threadcount = 5
_lock = Lock()
_executor = ThreadPoolExecutor(_threadcount)


def start(*args):
    with _lock:
        _executor.submit(*args)


def shutdown(reload):
    global _executor
    with _lock:
        _executor.shutdown(False)
        if reload:
            _executor = ThreadPoolExecutor(_threadcount)
