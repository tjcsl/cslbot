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
import importlib
import logging
from os.path import exists, join
from . import config, command, handler, hook, misc, modutils


def do_log(c, target, msg):
    logging.error(msg)
    c.privmsg(target, msg)


def load_modules(cfg, confdir, send=logging.error):
    modutils.init_aux(cfg['core'])
    modutils.init_groups(cfg['groups'], confdir)
    errored_commands = command.registry.scan_for_commands()
    if errored_commands:
        logging.error("Failed to load some commands.")
        for error in errored_commands:
            send("%s: %s" % error)
        return False
    errored_hooks = hook.registry.scan_for_hooks()
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
            server_send("%s\n" % msg)
        else:
            do_log(bot.connection, target, msg)
    confdir = bot.handler.confdir

    if cmdargs == 'pull':
        if exists(join(confdir, '.git')):
            send(misc.do_pull(srcdir=confdir))
        else:
            send(misc.do_pull(repo=bot.config['api']['githubrepo']))
    # Reload config
    importlib.reload(config)
    bot.config = config.load_config(join(confdir, 'config.cfg'), send)
    # Reimport helpers
    errored_helpers = modutils.scan_and_reimport('helpers')
    if errored_helpers:
        send("Failed to load some helpers.")
        for error in errored_helpers:
            send("%s: %s" % error)
        return False
    if not load_modules(bot.config, confdir, send):
        return False

    # preserve data
    data = bot.handler.get_data()
    bot.shutdown_mp()
    bot.handler = handler.BotHandler(bot.config, bot.connection, bot.channels, confdir)
    bot.handler.set_data(data)
    bot.handler.connection = bot.connection
    bot.handler.channels = bot.channels
    return True
