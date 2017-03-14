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

    def test_addpennies_success(self):
        result = self._test_program(rb"""
: main
    #0 "FooBar" newobject
    1
    over pennies 1 = and
    over 50 addpennies over pennies 51 = and
    if me @ "Test passed." notify then
;
""",before=rb"""
@set test.muf=W
""")

    def test_moveto_simple(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    me @ "SomeVehicle" newobject var! vehicle
    vehicle @ "V" set
    1
    obj @ location me @ = and
    obj @ #0 moveto obj @ location #0 = and
    obj @ vehicle @ moveto obj @ location vehicle @ = and
    vehicle @ contents obj @ = and
    if me @ "Test passed." notify then
;
""")
    
    def test_moveto_loop(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    obj @ "V" set
    me @ "SomeVehicle" newobject var! vehicle
    vehicle @ "V" set
    obj @ vehicle @ moveto
    0 try vehicle @ obj @ moveto catch
        "contain itself" instring if me @ "Test passed." notify then
    endcatch
;
""")

    def test_contents_list(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    {
        me @ "ThingOne" newobject dup obj @ moveto
        me @ "ThingTwo" newobject dup obj @ moveto
        me @ "ThingThree" newobject dup obj @ moveto
    }list 0 array_sort var! contained
    1
    obj @ contents contained @ swap array_findval array_count 0 > and
    obj @ contents next contained @ swap array_findval array_count 0 > and
    obj @ contents next next contained @ swap array_findval array_count 0 > and
    obj @ contents next next next #-1 = and
    obj @ contents_array 0 array_sort contained @ array_compare 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_exits_list(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    {
        obj @ "exitOne" newexit
        obj @ "exitTwo" newexit
        obj @ "exitThree" newexit
    }list 0 array_sort var! contained
    1
    obj @ exits contained @ swap array_findval array_count 0 > and
    obj @ exits next contained @ swap array_findval array_count 0 > and
    obj @ exits next next contained @ swap array_findval array_count 0 > and
    obj @ exits next next next #-1 = and
    obj @ exits_array 0 array_sort contained @ array_compare 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_lockedp(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    obj @ "_/lok" "_testprop:testval" parselock setprop
    1
    me @ obj @ locked? and
    me @ "_testprop" "testval" setprop me @ obj @ locked? not and
    if me @ "Test passed." notify then
;
""")

    def test_setgetlockstr(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    obj @ "_testprop:testval" setlockstr
    1
    obj @ "_/lok" getprop unparselock "_testprop:testval" parselock unparselock strcmp not and
    obj @ getlockstr "_testprop:testval" parselock unparselock strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_recycle_success(self):
        result = self._test_program(rb"""
: main
    me @ "FooBar" newobject var! obj
    1
    obj @ ok? and
    obj @ thing? and
    obj @ recycle
    obj @ ok? not and
    obj @ thing? not and
    if me @ "Test passed." notify then
;
""")

class TestMatch(MufProgramTestBase):
    def test_exits_attachments(self):
        self._test_program(rb"""
: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    #0 "alpha;bravo;charlie" newexit var! zeroExit
    1 
    "alpha" match zeroExit @ = and
    "bravo" match zeroExit @ = and
    "charlie" match zeroExit @ = and
    "delta" match #-1 = and
    testRoom @ "bravo;charlie;delta;echo" newexit var! roomExit
    "alpha" match zeroExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    me @ "alpha;charlie;echo;foxtrot;golf" newexit var! meExit
    "alpha" match meExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match meExit @ = and
    "golf" match meExit @ = and
    testRoom @ "SomeObject" newobject var! testObj
    testObj @ "alpha;bravo;echo;foxtrot" newexit var! testObjExit
    "alpha" match testObjExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match testObjExit @ = and
    "golf" match meExit @ = and
    me @ "SomeObjectTwo" newobject var! testInvObj
    testInvObj @ "alpha;bravo;echo;foxtrot;golf" newexit var! testInvObjExit
    "alpha" match testInvObjExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match testInvObjExit @ = and
    "golf" match testInvObjExit @ = and
    if me @ "Test passed." notify then
;
""")

    def test_things_priority(self):
        self._test_program(rb"""
: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    testRoom @ "TestObject" newobject var! roomObj
    1 
    "TestObject" match roomObj @ = and
    me @ "TestObject" newobject var! meObj
    "TestObj" match #-2 = and
    meObj @ "TestObject Longer" setname
    "TestObject" match roomObj @ = and
    "TestObject L" match meObj @ = and
    meObj @ "TestObject" setname
    roomObj @ "TestObject Longer" setname
    "TestObject" match meObj @ = and
    "TestObj" match #-2 = and
    "TestObject L" match roomObj @ = and
    if me @ "Test passed." notify then
;
""")

    def test_multiple_exact_is_random(self):
        self._test_program(rb"""
: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    testRoom @ "TestObject" newobject var! roomObj
    me @ "TestObject" newobject var! meObj
    0 var! count
    1
    begin
        "TestObject" match dup var! lastMatch roomObj @ = not while
        meObj @ = not if me @ "Test failed." exit then
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ roomObj @ = and
    begin
        "TestObject" match dup lastMatch ! meObj @ = not while
        roomObj @ = not if me @ "Test failed." exit then
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ meObj @ = and
    if me @ "Test passed." notify then
;
""")


class TestMisc(MufProgramTestBase):
    def test_dbref(self):
        self._test_program(rb"""
: main
    1
    0 dbref #0 = and
    42 dbref #42 = and
    42 dbref dbref? and
    -1 dbref #-1 = and
    if me @ "Test passed." notify then
;
""")

    def test_part_pmatch_self_only(self):
        self._test_program(rb"""
: main
    1
    "O" part_pmatch #1 = and
    "On" part_pmatch #1 = and
    "One" part_pmatch #1 = and
    "OneFoo" part_pmatch #-1 = and
    if me @ "Test passed." notify then
;
""")

    def test_checkpassword(self):
        self._test_program(rb"""
: main
    1
    #1 "potrzebie" checkpassword and
    #1 "notthis" checkpassword not and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
