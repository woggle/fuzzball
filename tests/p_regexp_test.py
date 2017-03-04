#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestRegexp(MufProgramTestBase):
    def test_regmatch_simple_true(self):
        result = self._test_program(b"""
: main
    "THIS is a test!" "is(.*)test" 0 regexp
    1
    over array_count 2 = and
    over 0 array_getitem { 6 9 }list array_compare 0 = and
    over 1 array_getitem { 8 3 }list array_compare 0 = and
    swap pop
    over array_count 2 = and
    over 0 array_getitem "is a test" strcmp not and
    over 1 array_getitem " a " strcmp not and
    swap pop
    if me @ "Test passed." notify then
;
""")

    def test_regsub_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "is(.*?)test" "X\\\\1Y" REG_ALL regsub
    "THIS X a Y! THIS X still a Y!" strcmp not 
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "THIS" regsplit
    { "" " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_noempty_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "THIS" regsplit_noempty
    { " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_nomatch(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "NEVER MATCHES" regsplit
    { "THIS is a test! THIS is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")
    def test_regsplit_capture(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "(TH.S)" regsplit
    { "" " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")
    def test_regsplit_invalid(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "(TH.S" 
    2 try regsplit catch
        if me @ "Test passed." notify then
    endcatch
;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
