# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

def gen_random(msg):
    #msg = quote(msg)
    if not msg:
        html = urlopen('ttp://www.random.org/integers/?num=1&min=1&max='
                   + '1000000000' + '&col=1&base=10&format=plain&rnd=new', 
                   timeout=2).read().decode()
        random = re.search('>(.*)<', html).group(1).replace('\\', '').strip()
    elif msg < 1000000000:
        html = urlopen('ttp://www.random.org/integers/?num=1&min=1&max='
                   + msg + '&col=1&base=10&format=plain&rnd=new', 
                   timeout=2).read().decode()
        random = re.search('>(.*)<', html).group(1).replace('\\', '').strip()
    else:
        html = urlopen('ttp://www.random.org/integers/?num=1&min=1&max='
                   + '1000000000' + '&col=1&base=10&format=plain&rnd=new', 
                   timeout=2).read().decode()
        random = re.search('>(.*)<', html).group(1).replace('\\', '').strip()


def cmd(send, msg, args):
    """Gets a random integer.
    Syntax: !random <maximum length>
    """
    random = gen_random(msg)
    send(random)
