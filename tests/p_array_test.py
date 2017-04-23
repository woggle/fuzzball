#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestArrayFlat(MufProgramTestBase):
    def test_array_notify(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
: main
    { "This is the first line." "This is the second line." }list
    { me @ }list array_notify
;
.
c
q
@set test.muf=D
@act runtest=me
@link runtest=test.muf
runtest
""")
        self.assertTrue(b'\nThis is the first line.' in result)
        self.assertTrue(b'\nThis is the second line.' in result)


class TestArrayFilterFlags(MufProgramTestBase):
    
    def test_simple(self):
        self._test_program(b"""
: main
    { #0 #1 #2 #3 #4 #5 }list "PW" array_filter_flags { #1 }list array_compare 0 =
    { #0 #1 #2 #3 #4 #5 }list "P!W" array_filter_flags { #4 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "P" array_filter_flags { #1 #4 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "R" array_filter_flags { #0 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "!T" array_filter_flags { #0 #1 #2 #3 #4 }list array_compare 0 = and
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""", before=b"""
@pcreate IdFour=test
@create IdFive
""")

class TestArrayProps(MufProgramTestBase):
    def test_array_get_propdirs_wizprops(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test/@doublesecret/foo" 3 setprop
    dup "_test/~unsecret/foo" 4 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" "@doublesecret" "~unsecret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""",before=b"@set test.muf=W")

    def test_array_get_propdirs_wizprops_unreadable(self):
        self._test_program(b"""
: main
    #2
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""",before=b"""
@create Foo
@set Foo=_test/@doublesecret:foo
@set Foo=_test/@doublesecret/bar:quux
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
