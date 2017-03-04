#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestSayPose(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
say Hello 1.
"Hello 2.
pose Hello 3.
:Hello 4.
  say Hello 5.
  "Hello 6.
    pose Hello 7.
    :Hello 8.
""")
        self.assertTrue(b'You say, "Hello 1."' in result)
        self.assertTrue(b'You say, "Hello 2."' in result)
        self.assertTrue(b'One Hello 3.' in result)
        self.assertTrue(b'One Hello 4.' in result)
        self.assertTrue(b'You say, "Hello 5."' in result)
        self.assertTrue(b'You say, "Hello 6."' in result)
        self.assertTrue(b'One Hello 7.' in result)
        self.assertTrue(b'One Hello 8.' in result)

class TestGripe(ServerTestBase):
    extra_params = {'file_log_gripes': 'logs/gripes'}
    def test(self):
        import os.path
        result = self._do_full_session(CONNECT_GOD +
b"""
gripe this is a gripe.
""")
        self.assertTrue(b'Your complaint has been' in result)
        with open(os.path.join(self.server.game_dir, 'logs', 'gripes'), 'r') as fh:
            log_text= fh.read()
        self.assertTrue('this is a gripe' in log_text)

class TestSinglePlayerPage(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
page One=This is a test.
""")
        self.assertTrue(b'One pages from Room Zero: "This is a test."' in result)

class TestSinglePlayerPageHaven(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@set me=H
page One=This is a test.
""")
        self.assertTrue(b'does not wish to be')

class TestSinglePlayerWhisper(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
whisper One=This is a test.
""")
        self.assertTrue(b'You whisper, "This is a test." to One' in result)
        self.assertTrue(b'One whispers, "This is a test."' in result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
