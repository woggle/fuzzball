#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestHuh(ServerTestBase):
    extra_params = {'huh_mesg': '### HUH ###'}
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
 asdfasdfasdf
""")
        self.assertTrue(b'### HUH ###' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
