# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
import configparser
import logging
from helpers import command, handler, hook, misc, modutils
from os import path


def do_log(c, target, msg):
    logging.error(msg)
    c.privmsg(target, msg)


def load_modules(config, send=logging.error):
    modutils.init_aux(config['core'])
    modutils.init_groups(config['groups'])
    errored_commands = command.scan_for_commands('commands')
    if errored_commands:
        logging.error("Failed to load some commands.")
        for error in errored_commands:
            send("%s: %s" % error)
        return False
    errored_hooks = hook.scan_for_hooks('hooks')
    if errored_hooks:
        logging.error("Failed to reload some hooks.")
        for error in errored_hooks:
            send("%s: %s" % error)
        return False
    return True


def do_reload(bot, target, cmdargs, server_send=None):
    """The reloading magic.

    | First, reload handler.py.
    | Then make copies of all the handler data we want to keep.
    | Create a new handler and restore all the data.
    """
    def send(msg):
        if server_send is not None:
            server_send(msg)
        else:
            do_log(bot.connection, target, msg)

    if cmdargs == 'pull':
        srcdir = path.dirname(path.abspath(__file__))
        send(misc.do_pull(srcdir, bot.connection.real_nickname))
    # Reimport helpers
    errored_helpers = modutils.scan_and_reimport('helpers', 'helpers')
    if errored_helpers:
        send("Failed to load some helpers.")
        for error in errored_helpers:
            send("%s: %s" % error)
        return False
    if not load_modules(bot.config, send):
        return False

    bot.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config_file = path.join(path.dirname(__file__), '../config.cfg')
    with open(config_file) as f:
        bot.config.read_file(f)
    # preserve data
    data = bot.handler.get_data()
    bot.shutdown_mp()
    bot.handler = handler.BotHandler(bot.config, bot.connection, bot.channels)
    bot.handler.set_data(data)
    bot.handler.connection = bot.connection
    bot.handler.channels = bot.channels
    return True
