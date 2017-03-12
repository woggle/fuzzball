#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD


class TestEdit(ServerTestBase):
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@program foo.muf
i
this was the first line
this was the second line
this was the third line
this was the fourth line
.
2 3 d
2 i
this was inserted before the second line
.
q
""",
b"""
@edit foo.muf
n
1 10 l
q
""", use_dump=use_dump)
        self.assertTrue(b'1: this was the first line' in result)
        self.assertTrue(b'2: this was inserted before the second line' in result)
        self.assertTrue(b'3: this was the fourth line' in result)
        self.assertTrue(b'3 lines displayed' in result)

    def test_dump(self):
        self._test(use_dump=True)

    def test_nodump(self):
        self._test(use_dump=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
