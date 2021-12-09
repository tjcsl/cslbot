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

import random

from ..helpers.command import Command

squirrels = [
    "http://images.cheezburger.com/completestore/2011/11/2/aa83c0c4-2123-4bd3-8097-966c9461b30c.jpg",
    "http://images.cheezburger.com/completestore/2011/11/2/46e81db3-bead-4e2e-a157-8edd0339192f.jpg",
    "http://28.media.tumblr.com/tumblr_lybw63nzPp1r5bvcto1_500.jpg",
    "http://i.imgur.com/DPVM1.png",
    "http://d2f8dzk2mhcqts.cloudfront.net/0772_PEW_Roundup/09_Squirrel.jpg",
    "http://www.cybersalt.org/images/funnypictures/s/supersquirrel.jpg",
    "http://www.zmescience.com/wp-content/uploads/2010/09/squirrel.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/sniper-squirrel.jpg",
    "http://1.bp.blogspot.com/_v0neUj-VDa4/TFBEbqFQcII/AAAAAAAAFBU/E8kPNmF1h1E/s640/squirrelbacca-thumb.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/soldier-squirrel.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/squirrelmobster.jpeg",
]


@Command(['next', 'shipit'], ['name'])
def cmd(send, _, args):
    """Ships a product.

    Syntax: {command}

    """
    send("{}! {}".format(args['name'].upper(), random.choice(squirrels)))
