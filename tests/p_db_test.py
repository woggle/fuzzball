#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestCopyObj(MufProgramTestBase):
    def test_copyobj(self):
        result = self._test_program(rb"""
: main
    "Foo" match copyobj var! obj
    1
    obj @ name "Foo" strcmp not and
    obj @ location me @ = and
    obj @ "_proplist/a" getprop "foo" strcmp not and
    obj @ "_proplist/b" getprop "bar" strcmp not and
    obj @ "_lockprop" getprop unparselock "me" parselock unparselock strcmp not and
    obj @ "~protectedprop" getprop #0 = and
    if me @ "Test passed." notify then
    obj @ "NewFoo" setname
;
""",before=rb"""
@create Foo
@desc Foo={null:to preserve}
@set Foo=@secretprop:42
@propset Foo=dbref:~protectedprop:#0
@propset Foo=lock:_lockprop:me
@set Foo=_proplist/a:foo
@set Foo=_proplist/b:bar
drop Foo
""", after=rb"""
ex NewFoo=/
""")
        self.assertTrue(rb'str /@secretprop' in result)



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

class TestToadNoRecycle(MufProgramTestBase):
    extra_params = { 'toad_recycle': 'no' }

    def test_toad_owning(self):
        result = self._test_program(rb"""
: main
    "TestUser" "foo" newplayer var! testUser
    "OtherUser" "bar" newplayer var! otherUser
    #0 "TestObject" newobject var! testObject
    testObject @ testUser @ setown
    otherUser @ testUser @ toadplayer
    1
    testUser @ thing? and
    testObject @ owner otherUser @ = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")



class TestMisc(MufProgramTestBase):
    def test_mlevel(self):
        self._test_program(rb"""
: main
    1
    #1 mlevel 3 = and
    prog mlevel 3 = and
    "mlev1.muf" match mlevel 1 = and
    "mlev2.muf" match mlevel 2 = and
    "highLevelExit" match mlevel 2 = and
    "normalExit" match mlevel 0 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@program mlev1.muf
.
q
@set mlev1.muf=1
@program mlev2.muf
.
q
@set mlev2.muf=2
@act highLevelExit=#0
@act normalExit=#0
@set highLevelExit=2
@set test.muf=W
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
