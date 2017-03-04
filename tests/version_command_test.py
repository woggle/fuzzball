#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestVersion(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@version
""")
        self.assertTrue(b'Version: ' in result)

class TestHashes(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@hashes all
""")
        self.assertTrue(
            re.search(rb'File\s+Hash', result)
        )
        self.assertTrue(
            re.search(rb'interface.c\s+[a-fA-F0-9]+', result)
        )

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
