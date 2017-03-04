#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD


class TestWHOOnePlayer(ServerTestBase):
    extra_params = {
        'who_doing': 'yes',
    }
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""@set me=_/do:Doing message.
!WHO
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            b'Player Name' in result
        )
        self.assertTrue(
            re.search(rb'\nOne.*0s\s*.*Doing message.', result)
        )


class TestWHOOnePlayerNoDoing(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""!WHO
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            re.search(rb'Player Name\s*Location\s*On For', result)
        )
        self.assertTrue(
            re.search(rb'\nOne.*\s*\[\s*0\s*\]\s*.*\s*(?:127\.|local|::1|0000:)', result)
        )


class TestWHOOnePlayerNoDoingNoWiz(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(
b"""
connect TestUser foo
@set me=_/do:This should not show.
WHO
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            b'Player Name' in result
        )
        # look for start of IPv4 or IPv6 localhost
        self.assertTrue(
            re.search(rb'\nTestUser.*0s', result)
        )
        self.assertFalse(
            re.search(rb'\nTestUser.*This should not', result)
        )

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
