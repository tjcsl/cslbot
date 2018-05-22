#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import logging
import os
import socket
import sys
import unittest
import warnings
from os.path import dirname, exists, join
from unittest import mock

# Make this work from git.
if exists(join(dirname(__file__), "../.git")):
    sys.path.insert(0, join(dirname(__file__), ".."))

warnings.simplefilter("default")
warnings.filterwarnings("ignore", category=ImportWarning, module="importlib")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="alembic")

from test.bot_test import BotTest  # noqa


class CoreTest(BotTest):

    def test_handle_nick(self):
        """Test the bot's ability to handle nick change events."""
        # We must be in a channel to track other people's joins
        self.join_channel(self.nick, "#test-channel2")
        self.join_channel("testnick", self.channel)
        self.join_channel("testnick", "#test-channel2")
        calls = self.send_msg("nick", "testnick", "testnick2")
        self.assertEqual(
            calls,
            [
                ("testnick", self.channel, 0, "testnick2", "nick"),
                ("testnick", "#test-channel2", 0, "testnick2", "nick"),
            ],
        )

    def test_handle_mode_tracking(self):
        """Test the bot's ability to keep track of mode changes."""
        self.assertNotIn("testnick", self.bot.handler.voiced["#test-channel"])
        self.assertNotIn("testnick", self.bot.handler.opers["#test-channel"])
        self.join_channel("testnick", "#test-channel")
        self.assertFalse(self.bot.handler.voiced["#test-channel"]["testnick"])
        self.assertFalse(self.bot.handler.opers["#test-channel"]["testnick"])

        calls = self.send_msg("mode", self.nick, "#test-channel", ["+v", "testnick"])
        self.assertEqual(calls, [("testBot", "#test-channel", 0, "+v testnick", "mode")])
        self.assertTrue(self.bot.handler.voiced["#test-channel"]["testnick"])
        self.log_mock.reset_mock()

        calls = self.send_msg("mode", self.nick, "#test-channel", ["+o", "testnick"])
        self.assertEqual(calls, [("testBot", "#test-channel", 0, "+o testnick", "mode")])
        self.assertTrue(self.bot.handler.opers["#test-channel"]["testnick"])

    def test_bot_reload(self):
        """Make sure the bot can reload without errors."""
        sock = socket.socket()
        port = self.bot.config.getint("core", "serverport")
        passwd = self.bot.config["auth"]["ctrlpass"]
        sock.connect(("localhost", port))
        msg = "%s\nreload" % passwd
        sock.send(msg.encode())
        output = "".encode()
        while len(output) < 20:
            output += sock.recv(4096)
        sock.close()
        self.setup_handler()
        self.assertEqual(output.decode(), "Password: \nAye Aye Capt'n\n")


class MorseTest(BotTest):

    def test_morse_encode(self):
        """Make sure the bot properly encodes morse."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!morse bob"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "-... --- -...", "privmsg"),
                ("testnick", "#test-channel", 0, "!morse bob", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.morse.gen_word")
    def test_morse_noarg(self, mock_gen_word):
        """Test morse with no arguments."""
        mock_gen_word.return_value = "test"
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!morse"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "- . ... -", "privmsg"),
                ("testnick", "#test-channel", 0, "!morse", "pubmsg"),
            ],
        )

    def test_morse_too_long(self):
        """Test morse with an overlength argument."""
        calls = self.send_msg(
            "pubmsg",
            "testnick",
            "#test-channel",
            [
                "!morse aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            ],
        )
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "Your morse is too long. Have you considered Western Union?",
                    "privmsg",
                ),
                (
                    "testnick",
                    "#test-channel",
                    0,
                    "!morse aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "pubmsg",
                ),
            ],
        )


class ZipcodeTest(BotTest):

    @mock.patch("cslbot.commands.zipcode.get")
    def test_zipcode_valid(self, mock_get):
        """Test a correct zip code."""
        with open(join(dirname(__file__), "data", "zipcode_12345.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())

        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!zipcode 12345"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "12345: Schenectady, NY", "privmsg"),
                ("testnick", "#test-channel", 0, "!zipcode 12345", "pubmsg"),
            ],
        )

    def test_zipcode_blank(self):
        """Test a blank zip code."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!zipcode"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "the following arguments are required: zipcode",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!zipcode", "pubmsg"),
            ],
        )

    def test_zipcode_invalid(self):
        """Test incorrect zip codes."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!zipcode potato"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "Couldn't parse a ZIP code from potato", "privmsg"),
                ("testnick", "#test-channel", 0, "!zipcode potato", "pubmsg"),
            ],
        )


class WisdomTest(BotTest):

    @mock.patch("cslbot.commands.wisdom.get")
    def test_wisdom_valid(self, mock_get):
        """Test a valid wisdom lookup."""
        with open(join(dirname(__file__), "data", "wisdom_asimov.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())

        calls = self.send_msg(
            "pubmsg", "testnick", "#test-channel", ["!wisdom --author Isaac Asimov"]
        )
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "One, a robot may not injure a human being, or through inaction, allow a human being to come to harm "
                    + "Two, a robot must obey the orders given it by human beings except where such orders would conflict with the First Law "
                    + "Three, a robot must protect its own existence as long as such protection does not conflict with the First or Second Laws. -- Isaac Asimov",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!wisdom --author Isaac Asimov", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.wisdom.get")
    def test_wisdom_invalid(self, mock_get):
        """Test wisdom with no results."""
        with open(join(dirname(__file__), "data", "wisdom_jibberjabber.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())

        calls = self.send_msg(
            "pubmsg", "testnick", "#test-channel", ["!wisdom --search jibberjabber"]
        )
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "No words of wisdom found", "privmsg"),
                ("testnick", "#test-channel", 0, "!wisdom --search jibberjabber", "pubmsg"),
            ],
        )

    def test_wisdom_author_nosearch(self):
        """Check that we error if we specify an author search with no terms."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!wisdom --author"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "No author specified", "privmsg"),
                ("testnick", "#test-channel", 0, "!wisdom --author", "pubmsg"),
            ],
        )

    def test_wisdom_search_nosearch(self):
        """Check that we error if we specify a search with no terms."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!wisdom --search"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "No search terms specified", "privmsg"),
                ("testnick", "#test-channel", 0, "!wisdom --search", "pubmsg"),
            ],
        )

    def test_wisdom_search_author_invalid(self):
        """Check that we error if we specify both search and author."""
        self.join_channel("testBot", "#test-channel")
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!wisdom --search --author"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "argument --author: not allowed with argument --search",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!wisdom --search --author", "pubmsg"),
            ],
        )


class DefinitionTest(BotTest):

    @mock.patch("cslbot.commands.define.get")
    def test_definition_valid(self, mock_get):
        """Test a valid definition."""
        with open(join(dirname(__file__), "data", "define_potato.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())

        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!define potato"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "potato, white potato, Irish potato, murphy, spud, tater: "
                    "an edible tuber native to South America; a staple food of Ireland",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!define potato", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.define.get")
    def test_definition_invalid(self, mock_get):
        """Test an invalid definition."""
        with open(join(dirname(__file__), "data", "define_potatwo.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!define potatwo"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "No results found for potatwo", "privmsg"),
                ("testnick", "#test-channel", 0, "!define potatwo", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.define.get")
    def test_definition_empty(self, mock_get):
        """Test an invalid definition."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!define"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "the following arguments are required: word",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!define", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.define.get")
    def test_definition_invalid_index(self, mock_get):
        """Test an invalid definition index."""
        with open(join(dirname(__file__), "data", "define_potato.xml")) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!define potato --entry 5"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "Invalid index 5 for term potato", "privmsg"),
                ("testnick", "#test-channel", 0, "!define potato --entry 5", "pubmsg"),
            ],
        )


class ErrnoTest(BotTest):

    @mock.patch("cslbot.helpers.misc.choice")
    def test_errno_valid_no_input(self, mock_choice):
        """Test errno run with no input, this also tests name -> number mapping."""
        mock_choice.return_value = "EOVERFLOW"
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!errno"])
        output = "Please install gcc." if os.name == "nt" else "#define EOVERFLOW 75"
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, output, "privmsg"),
                ("testnick", "#test-channel", 0, "!errno", "pubmsg"),
            ],
        )

    def test_errno_valid_number(self):
        """Test errno number -> name mapping."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!errno 75"])
        output = "Please install gcc." if os.name == "nt" else "#define EOVERFLOW 75"
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, output, "privmsg"),
                ("testnick", "#test-channel", 0, "!errno 75", "pubmsg"),
            ],
        )

    def test_errno_invalid_name(self):
        """Test errno run with an invalid name."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!errno ENOPANTS"])
        output = "Please install gcc." if os.name == "nt" else "ENOPANTS not found in errno.h"
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, output, "privmsg"),
                ("testnick", "#test-channel", 0, "!errno ENOPANTS", "pubmsg"),
            ],
        )

    def test_errno_list(self):
        """Test errno list command."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!errno list"])
        if os.name == "nt":
            expected = [("testBot", "#test-channel", 0, "Please install gcc.", "privmsg")]
        else:
            expected = [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "EACCES, EADDRINUSE, EADDRNOTAVAIL, EADV, EAFNOSUPPORT, EAGAIN, EALREADY, EBADE, EBADF, EBADFD, EBADMSG, "
                    + "EBADR, EBADRQC, EBADSLT, EBFONT, EBUSY, ECANCELED, ECHILD, ECHRNG, ECOMM, ECONNABORTED, ECONNREFUSED, ECONNRESET, "
                    + "EDEADLK, EDESTADDRREQ, EDOM, EDOTDOT, EDQUOT, EEXIST, EFAULT, EFBIG, EHOSTDOWN, EHOSTUNREACH, EHWPOISON, EIDRM, "
                    + "EILSEQ, EINPROGRESS, EINTR, EINVAL, EIO, EISCONN, EISDIR, EISNAM, EKEYEXPIRED, EKEYREJECTED,",
                    "privmsg",
                ),
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "EKEYREVOKED, ELIBACC, ELIBBAD, ELIBEXEC, ELIBMAX, ELIBSCN, ELNRNG, ELOOP, EMEDIUMTYPE, EMFILE, EMLINK, EMSGSIZE, "
                    + "EMULTIHOP, ENAMETOOLONG, ENAVAIL, ENETDOWN, ENETRESET, ENETUNREACH, ENFILE, ENOANO, ENOBUFS, ENOCSI, ENODATA, "
                    + "ENODEV, ENOENT, ENOEXEC, ENOKEY, ENOLCK, ENOLINK, ENOMEDIUM, ENOMEM, ENOMSG, ENONET, ENOPKG, ENOPROTOOPT, "
                    + "ENOSPC, ENOSR, ENOSTR, ENOSYS, ENOTBLK,...",
                    "privmsg",
                ),
            ]
        self.assertEqual(
            calls, expected + [("testnick", "#test-channel", 0, "!errno list", "pubmsg")]
        )


class SignalTest(BotTest):

    def test_signal_valid(self):
        """Test signal, basic check only since errno covers most of the backend."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!signal 9"])
        output = "Please install gcc." if os.name == "nt" else "#define SIGKILL 9"
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, output, "privmsg"),
                ("testnick", "#test-channel", 0, "!signal 9", "pubmsg"),
            ],
        )


class CoinTest(BotTest):

    @mock.patch("cslbot.commands.coin.choice")
    def test_coin_valid(self, mock_choice):
        """Test the default coin flip."""
        mock_choice.return_value = "heads"
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!coin"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "The coin lands on... heads", "privmsg"),
                ("testnick", "#test-channel", 0, "!coin", "pubmsg"),
            ],
        )

    def test_coin_noninteger(self):
        """Test a non-digit argument."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!coin potato"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "Not A Valid Positive Integer.", "privmsg"),
                ("testnick", "#test-channel", 0, "!coin potato", "pubmsg"),
            ],
        )

    def test_coin_negative(self):
        """Test a negative argument."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!coin -1"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "Negative Flipping requires the (optional) quantum coprocessor.",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!coin -1", "pubmsg"),
            ],
        )

    def test_coin_zero(self):
        """Test coin flipping with arguments."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!coin 0"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "The coins land on heads 0 times and on tails 0 times.",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!coin 0", "pubmsg"),
            ],
        )


class BotsnackTest(BotTest):

    def test_botsnack_valid_noargs(self):
        """Test botsnack with no arguments."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!botsnack"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "This tastes yummy!", "privmsg"),
                ("testnick", "#test-channel", 0, "!botsnack", "pubmsg"),
            ],
        )

    def test_botsnack_valid_args(self):
        """Test botsnack with arguments."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!botsnack potatoes"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "Potatoes tastes yummy!", "privmsg"),
                ("testnick", "#test-channel", 0, "!botsnack potatoes", "pubmsg"),
            ],
        )

    def test_botsnack_invalid_cannibal(self):
        """Test botsnack with the bot's nick as argument."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!botsnack testBot"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "wyang says Cannibalism is generally frowned upon.",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!botsnack testBot", "pubmsg"),
            ],
        )


class TranslateTest(BotTest):

    @unittest.skip("Need to figure out how to pass a valid api key")
    def test_translate_valid_args(self):
        """Test translate with a valid string."""
        calls = self.send_msg(
            "pubmsg", "testnick", "#test-channel", ["!translate --from de testen übersetzen"]
        )
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "Translation test", "privmsg"),
                (
                    "testnick",
                    "#test-channel",
                    0,
                    "!translate --from de testen übersetzen",
                    "pubmsg",
                ),
            ],
        )

    @unittest.skip("Need to figure out how to pass a valid api key")
    def test_translate_valid_to_lang(self):
        """Test translate with a valid 'to' language."""
        calls = self.send_msg(
            "pubmsg",
            "testnick",
            "#test-channel",
            ["!translate --from de --to es testen übersetzen"],
        )
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "prueba de traducción", "privmsg"),
                (
                    "testnick",
                    "#test-channel",
                    0,
                    "!translate --from de --to es testen übersetzen",
                    "pubmsg",
                ),
            ],
        )

    @mock.patch("cslbot.commands.translate.gen_translate")
    def test_translate_invalid_noargs(self, mock_gen_translate):
        """Test translate with no arguments."""
        mock_gen_translate.return_value = "test"
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!translate"])
        self.assertEqual(
            calls,
            [
                (
                    "testBot",
                    "#test-channel",
                    0,
                    "the following arguments are required: msg",
                    "privmsg",
                ),
                ("testnick", "#test-channel", 0, "!translate", "pubmsg"),
            ],
        )

    @unittest.skip("Need to figure out how to pass a valid api key")
    def test_translate_invalid_to_lang(self):
        """Test translate with an invalid 'to' language."""
        calls = self.send_msg(
            "pubmsg", "testnick", "#test-channel", ["!translate --to ad translate this"]
        )
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "translate this", "privmsg"),
                ("testnick", "#test-channel", 0, "!translate --to ad translate this", "pubmsg"),
            ],
        )


class FullwidthTest(BotTest):

    def test_fullwidth_ascii(self):
        """Test fullwidth with ASCII characters."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!fullwidth ayy lmao"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "ＡＹＹ\u3000ＬＭＡＯ", "privmsg"),
                ("testnick", "#test-channel", 0, "!fullwidth ayy lmao", "pubmsg"),
            ],
        )

    def test_fullwidth_nonascii(self):
        """Test fullwidth with non-ASCII characters."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!fullwidth ▲▢◎"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "▲▢◎", "privmsg"),
                ("testnick", "#test-channel", 0, "!fullwidth ▲▢◎", "pubmsg"),
            ],
        )

    @mock.patch("cslbot.commands.fullwidth.gen_word")
    def test_fullwidth_noarg(self, mock_gen_word):
        """Test fullwidth with no arguments."""
        mock_gen_word.return_value = "test"
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!fullwidth"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "ＴＥＳＴ", "privmsg"),
                ("testnick", "#test-channel", 0, "!fullwidth", "pubmsg"),
            ],
        )


class GrepTest(BotTest):

    def test_grep_fwilson(self):
        """Test grep with fwilson."""
        calls = self.send_msg("pubmsg", "testnick", "#test-channel", ["!grep fwilson"])
        self.assertEqual(
            calls,
            [
                ("testBot", "#test-channel", 0, "fwilson has never been said.", "privmsg"),
                ("testnick", "#test-channel", 0, "!grep fwilson", "pubmsg"),
            ],
        )


if __name__ == "__main__":
    loglevel = logging.DEBUG if "-v" in sys.argv else logging.INFO
    logging.basicConfig(level=loglevel)
    unittest.main()
