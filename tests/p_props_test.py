#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestManipObject(MufProgramTestBase):
    def test_props_getset(self):
        result = self._test_program(b"""
: main
    #0 "FooBar" newobject
    dup "_testint" 42 setprop
    dup "_testint2" "" 42 addprop
    dup "_teststr" "foobar" setprop
    dup "_teststr2" "foobar" 0 addprop
    dup "_testref" #0 setprop
    dup "_testlok" "me&!me" parselock setprop
    dup "_testflt" 42.0 setprop
    dup "_testdir/foo" 42 setprop
    dup "_testdir" 2 setprop
    dup "_testdir2/foo" 3 setprop
    1 
    over "_testint" getprop 42 = and
    over "_testint" getpropval 42 =  and
    over "_teststr" getprop "foobar" strcmp not and
    over "_teststr" getpropstr "foobar" strcmp not and
    over "_testref" getprop dup dbref? swap #0 = and and
    over "_testlok" getprop me @ swap testlock not and
    over "_testlok" getprop prettylock "One(#1PWM3)&!One(#1PWM3)" strcmp not and
    over "_testflt" getprop 42.0 = and
    over "_testflt" getpropfval 42.0 = and
    over "_noprop" getpropstr "" strcmp not and
    over "_testdir/foo" getprop 42 = and
    over "_testdir" getprop 2 = and
    over "_testdir2/foo" getprop 3 = and
    over "_testdir" propdir? and
    if me @ "Test passed." notify then
;
""", after=b"\nex FooBar=/\n") 
        self.assertTrue(b'- int /_testint:42' in result)
        self.assertTrue(b'- int /_testint2:42' in result)
        self.assertTrue(b'- str /_teststr:foobar' in result)
        self.assertTrue(b'- str /_teststr2:foobar' in result)
        self.assertTrue(b'- ref /_testref:Room Zero' in result)
        self.assertTrue(b'- lok /_testlok:' in result)
        self.assertTrue(b'- int /_testdir/:2' in result)
        self.assertTrue(b'- dir /_testdir2/:(no value)' in result)


    def test_props_nextprop_nowiz(self):
        result = self._test_program(b"""
: main
    "FooBar" match var! theThing
    1
    "" { }list var! lst
    begin 
        theThing @ swap nextprop dup while
        dup lst @ array_appenditem lst !
    repeat
    pop
    lst @ { "/_bar" "/_foo" "/_quux" }list
    array_compare 0 = and

    "/_foo/" { }list lst !
    begin 
        theThing @ swap nextprop dup while
        dup lst @ array_appenditem lst !
    repeat
    pop
    lst @ { "/_foo/.alpha" "/_foo/beta" "/_foo/delta" }list
    array_compare 0 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@create FooBar
@set FooBar=_foo/.alpha:1
@set FooBar=_foo/beta:1
@set FooBar=_foo/delta:1
@set FooBar=_foo/@hidden:none
@set FooBar=@hidden:none
@set foobar=_bar:1
@set foobar=_quux:1
""")

    def test_props_nextprop_wiz(self):
        result = self._test_program(b"""
: main
    "FooBar" match var! theThing
    1
    "" { }list var! lst
    begin 
        theThing @ swap nextprop dup while
        dup lst @ array_appenditem lst !
    repeat
    pop
    lst @ { "/@" "/@hidden" "/_bar" "/_foo" "/_quux" }list
    array_compare 0 = and

    "/_foo/" { }list lst !
    begin 
        theThing @ swap nextprop dup while
        dup lst @ array_appenditem lst !
    repeat
    pop
    lst @ { "/_foo/.alpha" "/_foo/@hidden"  "/_foo/beta" "/_foo/delta" }list
    array_compare 0 = and
    if me @ "Test passed." notify then
;
""", before=rb"""
@create FooBar
@set FooBar=_foo/.alpha:1
@set FooBar=_foo/beta:1
@set FooBar=_foo/delta:1
@set FooBar=_foo/@hidden:none
@set FooBar=@hidden:none
@set foobar=_bar:1
@set foobar=_quux:1
@set test.muf=W
""")

    def test_remove_prop(self):
        result = self._test_program(b"""
: main
    #0 "FooBar" newobject var! theThing
    1
    theThing @ "_testprop1" "testvalue" setprop
    theThing @ "_testdir/alpha" "me&!me" parselock setprop
    theThing @ "_testdir/beta" 2.0 setprop
    theThing @ "_testdir/delta/gamma" "testValueOther" setprop
    theThing @ "_testdir2/alpha" #42 setprop
    theThing @ "_testdir2" "value" setprop

    theThing @ "_testprop1" getprop and
    theThing @ "_testprop1" remove_prop
    theThing @ "_testprop1" getprop not and
    
    theThing @ "_testdir/delta/gamma" getprop and
    theThing @ "_testdir" remove_prop
    theThing @ "_testdir/delta/gamma" getprop not and
    theThing @ "_testdir/beta" getprop not and
    theThing @ "_testdir/alpha" getprop not and

    theThing @ "_testdir2/alpha" getprop and
    theThing @ "_testdir2" remove_prop
    theThing @ "_testdir2/alpha" getprop not and
    theThing @ "_testdir2" getprop not and
    if me @ "Test passed." notify then
;
""")


class TestEnvProp(MufProgramTestBase):
    SETUP = rb"""
: main
    1
    me @ "FooBar" newobject var! theThing
    #0 "SecondEnv" newroom var! secondEnv
    secondEnv @ "ThirdEnv" newroom var! thirdEnv
    me @ thirdEnv @ moveto
"""
    def test_direct(self):
        result = self._test_program(SETUP + rb"""
    me @ "_testprop" "onMe" setprop
    thirdEnv @ "_testprop" "onThird" setprop
    me @ "_testprop" envprop "onMe" strcmp not swap #1 = and and
    me @ "_testprop" envpropstr "onMe" strcmp not swap #1 = and and

    if me @ "Test passed." notify then
;
""")

    def test_root(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    me @ "_testprop" envprop "onZero" strcmp not swap #0 = and and
    me @ "_testprop" envpropstr "onZero" strcmp not swap #0 = and and

    if me @ "Test passed." notify then
;
""")

    def test_middle(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    secondEnv @ "_testprop" "onSecond" setprop
    me @ "_testprop" envprop "onSecond" strcmp not swap secondEnv @ = and and

    if me @ "Test passed." notify then
;
""")

    def test_lock(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    secondEnv @ "_testprop" "me" parselock setprop
    me @ "_testprop" envprop unparselock "me" parselock unparselock strcmp not
        swap secondEnv @ = and and
    me @ "_testprop" envpropstr "me" parselock prettylock strcmp not
        swap secondEnv @ = and and

    if me @ "Test passed." notify then
;
""")

    def test_dbref(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    secondEnv @ "_testprop" #42 setprop
    me @ "_testprop" envprop #42 = 
        swap secondEnv @ = and and
    me @ "_testprop" envpropstr "#42" strcmp not
        swap secondEnv @ = and and

    if me @ "Test passed." notify then
;
""")
    
    def test_end(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    secondEnv @ "_testprop" "onSecond" setprop
    thirdEnv @ "_testprop" "onThird" setprop
    me @ "_testprop" envprop "onThird" strcmp not swap thirdEnv@ = and and

    if me @ "Test passed." notify then
;
""")

    def test_thing_in_player(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    me @ "_testprop" "onMe" setprop
    theThing @ "_testprop" envprop "onMe" strcmp not swap me @ = and and
    theThing @ "_testprop" envpropstr "one me" strcmp not swap me @ = and and

    if me @ "Test passed." notify then
;
""")

    def test_thing_in_player_room(self):
        result = self._test_program(SETUP + rb"""
    #0 "_testprop" "onZero" setprop
    thirdEnv @ "_testprop" "onThird" setprop
    theThing @ "_testprop" envprop "onThird" strcmp not swap thirdEnv @ = and and
    theThing @ "_testprop" envpropstr "onThird" strcmp not swap thirdEnv @ = and and

    if me @ "Test passed." notify then
;
""")

class TestArrayFilterProp(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    1

    me @ "ThingOne" newobject var! obj1
    me @ "ThingTwo" newobject var! obj2
    me @ "ThingThree" newobject var! obj3

    obj1 @ "_testprop" "foobar" setprop
    obj2 @ "_testprop" "bar" setprop
    obj3 @ "_testprop" "quux" setprop

    { obj1 @ obj2 @ obj3 @ }list
    "_testprop"
    "*bar*"
    array_filter_prop
    { obj1 @ obj2 @ }list array_compare 0 = and

    { obj1 @ obj2 @ obj3 @ }list
    "_testprop"
    "*notpresent*"
    array_filter_prop
    { }list array_compare 0 = and

    if me @ "Test passed." notify then
;
""")

    def test_no_perms(self):
        result = self._test_program(rb"""
: main
    1

    { me @ }list "@exampleprop" "*" array_filter_prop
    { }list array_compare 0 = and
    
    { me @ }list "@otherexampleprop" "*" array_filter_prop
    { }list array_compare 0 = and

    if me @ "Test passed." notify then
;
""", before=rb"""
@set me=@exampleprop:value
""")

    def test_non_strings(self):
        result = self._test_program(rb"""
: main
    1

    me @ "ThingOne" newobject var! obj1
    me @ "ThingTwo" newobject var! obj2
    me @ "ThingThree" newobject var! obj3
    me @ "ThingFour" newobject var! obj4

    obj1 @ "_testprop" 4200 setprop
    obj2 @ "_testprop" #1242 setprop
    obj3 @ "_testprop" "contains 42" setprop
    obj4 @ "_testprop" "_test00042:yes" parselock setprop

    { obj1 @ obj2 @ obj3 @ obj4 @ }list
    "_testprop"
    "*42*"
    array_filter_prop
    { obj1 @ obj2 @ obj3 @ obj4 @ }list array_compare 0 = and

    { obj1 @ obj2 @ obj3 @ obj4 @ }list
    "_testprop"
    "*notpresent*"
    array_filter_prop
    { }list array_compare 0 = and

    if me @ "Test passed." notify then
;
""")


class TestRefList(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    1

    me @ "_testprop" "#42 #43 #50 #7" setprop
    me @ "_testprop" #42 reflist_find 1 = and
    me @ "_testprop" #7 reflist_find 4 = and
    me @ "_testprop" #90 reflist_add
    me @ "_testprop" getprop "#42 #43 #50 #7 #90" strcmp not and
    me @ "_testprop" #50 reflist_del
    me @ "_testprop" getprop "#42 #43 #7 #90" strcmp not and

    if me @ "Test passed." notify then
;
""")


class TestBlessUnbless(MufProgramTestBase):
    def test_blessunbless(self):
        result = self._test_program(b"""
: main
    1
    me @ "_this_is_not_really_a_property" blessed? 0 = and
    me @ "_testprop" "{store:42,@secretProp}" setprop
    me @ "_testprop" blessed? 0 = and
    me @ "_testprop" "this is how" 0 parseprop pop
    me @ "@secretProp" getprop 0 = and
    me @ "_testprop" blessprop
    me @ "_testprop" blessed? 1 = and
    me @ "_testprop" "this is how" 0 parseprop pop
    me @ "@secretProp" getprop "42" strcmp not and
    me @ "_testprop" unblessprop
    me @ "_testprop" blessed? 0 = and

    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

class TestRunMPI(MufProgramTestBase):
    def test_parseprop_with_delay(self):
        result_main, result_user = self._second_user_test(b"""
@program test.muf
1 i
: main
    1
    me @ "_testprop" "{null:{store:42,_value}}HOW:{&how}{null:{delay:0,DELAY:{&how}}}" setprop
    me @ "_testprop" "how1" 0 parseprop "HOW:how1" strcmp not and
    0 sleep
    me @ "_value" getpropstr "42" strcmp not and
    me @ "_testprop" "how2" 1 parseprop "HOW:how2" strcmp not and
    0 sleep
    if me @ "Test passed." notify then
    1 sleep "TestUser" match descr_array foreach swap pop descrboot repeat
;
.
c
q
@act runtest=me
@set test.muf=W
@link runtest=test.muf
runtest
""")
        self.assertTrue(b'Test passed' in result_main)
        self.assertTrue(b'DELAY:how2' in result_main)
        self.assertTrue(b'One DELAY:how1' in result_user)

    def test_parsepropex_vars(self):
        result = self._test_program(b"""
: main
    1
    me @ "_testprop" "{&foo}/{&bar}{null:{set:quux,value of quux}}" setprop
   
    me @ "_testprop" 
    {
        "foo" "value of foo"
        "bar" "value of bar"
        "quux" "unknown"
    }dict 1 parsepropex
    "value of foo/value of bar" strcmp not
    over "quux" array_getitem "value of quux" strcmp not and
    over "foo" array_getitem "value of foo" strcmp not and
    swap pop
    and

    if me @ "Test passed." notify then
;
""")

    def test_parsempi(self):
        result = self._test_program(rb"""
: main
    1

    me @ "{null:{store:{&how},_testprop}}the value" "argument value" 0 parsempi
    "the value" strcmp not and
    me @ "_testprop" getprop "argument value" strcmp not and

    me @ "{null:{store:{&how},@testprop}}the value" "other argument value" 0 parsempi pop
    me @ "@testprop" getprop 0 =  and

    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_parsempiblessed(self):
        result = self._test_program(rb"""
: main
    1

    me @ "{null:{store:{&how},@testprop}}the value" "argument value" 0 parsempiblessed
    "the value" strcmp not and
    me @ "@testprop" getprop "argument value" strcmp not and

    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
