#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class TestWHOOnePlayer(ServerTestBase):
    def test_connect_God(self):
        result = self._do_full_session(CONNECT + 
b"""!WHO
QUIT
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
            b'One ' in result
        )
        self.assertTrue(
            b' 0s' in result # idle format
        )
        self.assertTrue(
            b'Come back later!' in result
        )

class TestBlankAction(ServerTestBase):
    def test_action(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo=me
@link foo=me
@lock foo=me&!me
@fail foo=Triggered failure message arg="{&arg}"
@succ foo=Triggered success message.
@set foo=H
foo Arguments here
QUIT
""")
        self.assertTrue(b'Triggered failure message arg="Arguments here"' in result)

class TestMPIOverflow(ServerTestBase):
    def test_action(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo=me
@link foo=me
@lock foo=me&!me
@fail foo={exec:_/fl}
@set foo=H
foo 
QUIT
""")
        self.assertTrue(b' Recursion limit exceeded.' in result)

class TestMPIForceOverflow(ServerTestBase):
    def test_action(self):
        result1 = self._do_full_session(CONNECT +
b"""
@pcreate TestPlayer=test
@action foo=here
@link foo=here
@lock foo=me&!me
@fail foo={force:*TestPlayer,foo}
@bless foo=_/fl
@set foo=H
QUIT
""")
        result2 = self._do_full_session(
b"""connect TestPlayer test
foo 
QUIT
""")
        logging.debug("result2 = %s", result2);
        self.assertTrue(b"You can't force recursively" in result2)

class TestMPILockOverflow(ServerTestBase):
    def test_action(self):
        result1 = self._do_full_session(CONNECT +
b"""
@action foo=here
@link foo=here
@lock foo=_fooprop:42
@set foo=_fooprop:{if:{locked:me,#2},42,0}
@succ foo=Foo success.
@fail foo=Foo failure.
foo
QUIT
""")
        logging.debug("result1 = %s", result1);
        self.assertTrue(b'Foo failure.' in result1)
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
