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
        "TestObject" match dup var! lastMatch meObj @ = while
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ roomObj @ = and
    begin
        "TestObject" match dup lastMatch ! roomObj @ = while
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ meObj @ = and
    if me @ "Test passed." notify then
;
""")

    def test_rmatch(self):
        self._test_program(rb"""
: main
    #0 "TestRoom" newroom var! testRoom
    1
    testRoom @ "TestRoom" rmatch #-1 = and
    testRoom @ "TestObject" newobject var! testObject
    testRoom @ "TestObject" rmatch testObject @ = and
    testObject @ me @ moveto
    testRoom @ "TestObject" rmatch #-1 = and
    testRoom @ "testExit;otherTestExit" newexit var! testExit
    testRoom @ "otherTestExit" rmatch testExit @ =  and
    testRoom @ "testExit" rmatch testExit @ = and
    testExit @ testObject @ moveto
    testObject @ testRoom @ moveto
    testRoom @ "testExit" rmatch #-1 = and
    testRoom @ "TestOther" newobject var! otherTestObject
    testRoom @ "TestO" rmatch #-2 = and
    if me @ "Test passed." notify then
;
""")

class TestFlags(MufProgramTestBase):
    def test_default_flags(self):
        self._test_program(rb"""
: main
    #0 "TestRoom" newroom var! testRoom
    #0 "TestThing" newobject var! testObject
    1
    { "dark" "abode" "chown_ok" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "mucker" "nucker" "sticky" "wizard" "truewizard" "zombie" }list
    foreach swap pop testRoom @ swap flag? 0 = and repeat
    { "dark" "abode" "chown_ok" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "mucker" "nucker" "sticky" "vehicle" "wizard" "truewizard" "xforcible" "zombie" }list
    foreach swap pop testObject @ swap flag? 0 = and repeat
    { "dark" "abode" "color" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "sticky" "zombie" "quell" "interactive" }list
    foreach swap pop #1 swap flag? 0 = and repeat
    #1 "mucker" flag? 1 = and
    #1 "nucker" flag? 1 = and
    #1 "wizard" flag? 1 = and
    me @ "interactive" flag? 0 = and
    prog "viewable" flag? and
    prog "silent" flag? not and
    prog "debug" flag? prog "dark" flag? = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
@set test.muf=V
""")

    def test_quell(self):
        self._test_program(rb"""
: main
    1
    "TestWizard" match "wizard" flag? 0 = and
    "TestWizard" match "truewizard" flag? 1 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
@pcreate TestWizard=foobar
@set TestWizard=W
@force TestWizard=@set me=Q
""")

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


class TestCopyPlayer(MufProgramTestBase):
    def test(self):
        result = self._test_program(rb"""
: main
    "TestUser" "foo" newplayer var! testUser
    #0 "TestRoom" newroom var! testRoom
    testUser @ "_someprop" 42 setprop
    testUser @ "~other/foobar/baz" 50 setprop
    testUser @ "~other/foobar" "test" setprop
    testUser @ testRoom @ setlink
    testUser @ "CopiedUser" "bar" copyplayer var! copiedUser
    testUser @ "TestObject" newobject
    1
    copiedUser @ getlink testRoom @ = and
    copiedUser @ "_someprop" getprop 42 = and
    copiedUser @ "~other/foobar" getprop "test" strcmp not and
    copiedUser @ "~other/foobar/baz" getprop 50 = and
    copiedUser @ "bar" checkpassword 1 = and
    copiedUser @ contents #-1 = and
    copiedUser @ location testRoom @ = and
    #0 contents #-1 = not and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

class TestProgramWriting(MufProgramTestBase):
    def test_read_write_compile_uncompile(self):
        self._test_program(rb"""
: main
    1
    prog compiled? and
    "tempprogram.muf" newprogram var! testprog
    testprog @ compiled? not and
    testprog @ {
        ": foo"
        "    42"
        ";"
        "PUBLIC foo"
        ": main 0 ;"
    }list dup var! progtext program_setlines
    testprog @ 0 0 program_getlines progtext @ array_compare 0 = and
    testprog @ compiled? not and
    testprog @ 0 compile 0 > and
    testprog @ compiled? and
    testprog @ uncompile
    testprog @ compiled? not and
    testprog @ "foo" call 42 = and
    testprog @ compiled? and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
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

    def test_nextowned(self):
        self._test_program(rb"""
: main
    1
    #0 "TestObjectOne" newobject var! testObjectOne
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    testPlayer @ nextowned #-1 = and
    testObjectOne @ testPlayer @ setown
    testPlayer @ nextowned testObjectOne @ = and
    testObjectOne @ nextowned #-1 = and
    #0 "TestObjectTwo" newobject var! testObjectTwo
    testObjectTwo @ testPlayer @ setown
    { testPlayer @ nextowned dup nextowned dup nextowned }list
    0 array_sort
    { testObjectOne @ testObjectTwo @ #-1 }list
    0 array_sort
    array_compare 0 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_setname_player(self):
        self._test_program(rb"""
: main
    1
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    0 try testPlayer @ "NewName" setname catch
        "requires password" instring and
    endcatch
    0 try testPlayer @ "One dumbpassword" setname catch
        "can't give a player that name" instring and
    endcatch
    0 try testPlayer @ "NewName wrongpassword" setname catch
        "Incorrect password" instring and
    endcatch
    testPlayer @ name "TestPlayer" strcmp not and
    testPlayer @ "NewName dumbpassword" setname
    testPlayer @ name "NewName" strcmp not and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_pmatch(self):
        self._test_program(rb"""
: main
    1
    "One" pmatch #1 = and
    "TestPlayer" pmatch #-1 = and
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    "TestPlayer" pmatch testPlayer @ = and
    testPlayer @ "NewName dumbpassword" setname
    "TestPlayer" pmatch #-1 = and
    "NewName" pmatch testPlayer @ = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

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

    def test_typep(self):
        self._test_program(rb"""
: main
    1
    #0 player? not and
    #0 thing? not and
    #0 room? and
    #0 program? not and
    #0 exit? not and
    #0 ok? and
    #1 player? and
    #1 thing? not and
    #1 room? not and
    #1 program? not and
    #1 exit? not and
    #1 ok? and
    prog player? not and
    prog thing? not and
    prog room? not and
    prog program? and
    prog exit? not and
    prog ok? and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_exit_links(self):
        self._test_program(rb"""
: main
    1
    #0 "testExit" newexit var! theExit
    #0 "otherExit" newexit var! otherExit
    theExit @ getlink #-1 = and
    theExit @ getlinks 0 = and
    theExit @ getlinks_array array_count 0 = and
    theExit @ #0 setlink
    theExit @ getlink #0 = and
    theExit @ getlinks 1 = swap #0 = and and
    theExit @ getlinks_array { #0 }list array_compare 0 = and
    theExit @ { otherExit @ #0 }list setlinks_array
    theExit @ getlinks_array { otherExit @ #0 }list array_compare 0 = and
    theExit @ getlinks array_make { otherExit @ #0 }list array_compare 0 = and
    theExit @ getlink otherExit @ = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_call_objmem(self):
        self._test_program(rb"""
: main
    1
    #0 objmem 0 > if me @ "Test passed." notify then
;
""")

    def test_instances(self):
        self._test_program(rb"""
: main
    1
    prog instances 1 = and
    "tempprogram.muf" newprogram var! testprog
    testprog @ instances 0 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_selfpid(self):
        self._test_program(rb"""
: main
    1
    getpids { pid }list array_compare 0 = and
    if me @ "Test passed." notify then
;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
