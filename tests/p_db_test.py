#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestManipObject(MufProgramTestBase):
    def test_create(self):
        result = self._test_program(b"""
: main
    #0 "FooBar" newobject
    dup #4 = ( #2 is test.muf; #3 is action to run)
    over thing? and
    over location #0 = and
    over owner #1 = and
    over #1 swap controls and
    over pennies 1 = and
    if me @ "Test passed." notify then
;
""", after=b"\nex FooBar\n")
        self.assertTrue(b'Type: THING' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
