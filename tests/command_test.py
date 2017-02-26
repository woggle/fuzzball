#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class TestWHOOnePlayer(ServerTestBase):
    def test(self):
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


class TestExamineActionSimple(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@dig Alpha
@action foo=me
@link foo=#2
@succ foo={null:success}
@osucc foo={null:osuccess}
@fail foo={null:failure}
@ofail foo={null:ofailure}
foo
foo
examine foo
QUIT
""")
        self.assertTrue(b'foo(#3E)  Owner: One' in result)
        self.assertTrue(b'Type: EXIT/ACTION' in result)
        self.assertTrue(b'Source: One(#1P' in result)
        self.assertTrue(b'Destination: Alpha(#2R' in result)
        self.assertTrue(b'Success: {null:success}' in result)
        self.assertTrue(b'Osuccess: {null:osuccess}' in result)
        self.assertTrue(b'Fail: {null:failure}' in result)
        self.assertTrue(b'Ofail: {null:ofailure}' in result)
        self.assertTrue(b'Usecount: 2' in result)


class TestExamineRoomSimple(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@dig Alpha=#0
@dig Beta=#2
@desc #3={null:Test description with MPI.}
examine #3
QUIT
""")
        self.assertTrue(b'Parent: Alpha(#2' in result)
        self.assertTrue(b'\r\n{null:Test description with MPI.}' in result)
        self.assertTrue(b'Owner: One' in result)
        self.assertTrue(b'Type: ROOM' in result)
        self.assertTrue(b'No exits.' in result)

class TestCreateExaminePlayer(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@dig Alpha=#0
@tune player_start=#2
@tune start_pennies
@pcreate TestPlayer=test
@desc *TestPlayer={null:Test description with MPI.}
@create Foo
@tel Foo=*TestPlayer
@dig Beta=#0
@act testAct=#3
@tel *TestPlayer=#5
examine *TestPlayer
QUIT
""")
        self.assertTrue(b'TestPlayer(#3PBH' in result)
        self.assertTrue(b'CPENNIES: 169' in result)
        self.assertTrue(b'\r\n{null:Test description with MPI.}' in result)
        self.assertTrue(b'Type: PLAYER' in result)
        self.assertTrue(b'Home: Alpha(#2R' in result)
        self.assertTrue(b'Location: Beta(#5R' in result)
        self.assertTrue(b'Carrying:\r\nFoo(#4)' in result)
        self.assertTrue(b'Actions/exits:\r\ntestAct(#6E' in result)

 
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
