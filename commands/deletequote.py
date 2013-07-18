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

args = ['srcdir', 'nick', 'admins']

def deletequote(key, args):
    quotefile = args['dir'] + "/quotes"
    quotes = json.load(open(quotefile))
    quotes.remove(quotes[key])
    f = open(quotefile, "w")
    json.dump(quotes, f)
    f.write("\n")
    f.close()

def cmd(send, msg, args):
    if args['nick'] in args['admins']:
        try:
            deletequote(msg, args)
            send("Deleted quote successfully")
        except ValueError:
            send("Not a valid quote id")
        except OSError:
            send("Nobody has taste in this channel")
    else:
        send("No.")