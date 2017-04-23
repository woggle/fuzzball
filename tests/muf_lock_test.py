#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestParseUnparseLock(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    "(me|_foo:bar)&(!me|_foo:baz)" parselock
    1
    over prettylock "(One(#1PWM3)|_foo:bar)&(!One(#1PWM3)|_foo:baz)" strcmp not and
    over unparselock "(#1|_foo:bar)&(!#1|_foo:baz)" strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_overflow_unparse(self):
        self._test_program(rb"""
: main
    0 try
        0 var lastlen lastlen !
        "me" begin
            "&!me" strcat
            dup parselock unparselock strlen
            dup lastlen @ = not while
            lastlen !
        repeat
    catch pop endcatch
    me @ "Test passed." notify
;
""", debug=False, timeout=20)

    def test_overflow_pretty(self):
        self._test_program(rb"""
: main
    0 try
        0 var lastlen lastlen !
        "me" begin
            "&!me" strcat
            dup parselock prettylock strlen
            dup lastlen @ = not while
            lastlen !
        repeat
    catch pop endcatch
    me @ "Test passed." notify
;
""")
    
    # this used to do an out-of-bounds read
    def test_malformed_regression_1(self):
        self._test_program(rb"""
: main
   "#3&" parselock not if me @ "Test passed." notify then
;
""")

class TestTestLock(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    #0 "TheRoom" newroom var troom troom !
    troom @  "Foo" newobject var tobj tobj !
    tobj @ "_example_prop_one" "test" setprop
    tobj @ "_example_prop_two" "{if:{eq:{&how},(Lock)},test,bad}" setprop

    1
    
    tobj @ "%d" fmtstring parselock
    tobj @ swap testlock and

    "#0" parselock
    tobj @ swap testlock not and

    troom @ "%d" fmtstring parselock
    tobj @ swap testlock and

    troom @ tobj @ "%d&%d" fmtstring parselock
    tobj @ swap testlock and

    troom @ tobj @ "%d|!%d" fmtstring parselock
    tobj @ swap testlock and
    
    troom @ tobj @ "!%d|!%d" fmtstring parselock
    tobj @ swap testlock not and
    
    tobj @ "!%d" fmtstring parselock
    tobj @ swap testlock not and

    "_example_prop_one:test" parselock
    tobj @ swap testlock and

    "_example_prop_two:test" parselock
    tobj @ swap testlock and

    "_example_prop_two:bad" parselock
    tobj @ swap testlock not and

    if me @ "Test passed." notify then
;
""")

    def test_program(self):
        self._test_program(rb"""
: main
    me @ thing? if
        me @ "_testprop" getprop
    else
        #0 "TheRoom" newroom var troom troom !
        troom @  "Foo" newobject var tobj tobj !
        1

        prog "%d" fmtstring parselock
        tobj @ swap testlock not and 

        tobj @ "_testprop" 1 setprop
        
        prog "%d" fmtstring parselock
        tobj @ swap testlock and 
    
        if me @ "Test passed." notify then
    then
;
""")

    def test_program_via_mpi(self):
        self._test_program(rb"""
: main
    me @ thing? if
        me @ "_testprop" getprop if "yes" else "no" then
    else
        #0 "TheRoom" newroom var troom troom !
        troom @  "Foo" newobject var tobj tobj !
        1

        tobj @ "_testprop2" prog "{muf:%d,}" fmtstring setprop

        "_testprop2:yes" parselock
        tobj @ swap testlock not and 

        tobj @ "_testprop" 1 setprop
        
        "_testprop2:yes" parselock
        tobj @ swap testlock and 
    
        if me @ "Test passed." notify then
    then
;
""")

    def test_overnesting(self):
        self._test_program(rb"""
: main
    me @ thing? if
        me @ prog "%d" fmtstring parselock testlock
    else
        #0 "TheRoom" newroom var troom troom !
        troom @  "Foo" newobject var tobj tobj !
        1

        prog "%d" fmtstring parselock
        tobj @ swap testlock not and 

        if me @ "Test passed." notify then
    then
;
""")

    def test_overnesting_mpi_calls_muf(self):
        self._test_program(rb"""
: main
    me @ thing? if
        me @ "_test_prop:test" fmtstring parselock testlock
        if "yes" else "no" then
    else
        #0 "TheRoom" newroom var troom troom !
        troom @  "Foo" newobject var tobj tobj !
        1

        tobj @ "_test_prop" prog "{muf:%d,}" fmtstring setprop
        prog "_test_prop:yes" fmtstring parselock
        tobj @ swap testlock not and 

        if me @ "Test passed." notify then
    then
;
""")

    def test_mpi_calls_mpi(self):
        self._test_program(rb"""
: main
    #0 "TheRoom" newroom var troom troom !
    troom @  "Foo" newobject var tobj tobj !
    1

    tobj @ "_thelock" "_test_prop2:yes" parselock setprop
    tobj @ "_test_prop" tobj @ "{if:{testlock:%d,_thelock},yes,no}" fmtstring setprop
    "_test_prop:yes" parselock
    tobj @ swap testlock not and 

    tobj @ "_test_prop2" "{null:with MPI}yes" setprop
    "_test_prop:yes" parselock
    tobj @ swap testlock and 

    if me @ "Test passed." notify then
;
""")



    def test_overnesting_mpi_calls_mpi(self):
        self._test_program(rb"""
: main
    #0 "TheRoom" newroom var troom troom !
    troom @  "Foo" newobject var tobj tobj !
    1

    tobj @ "_thelock" "_test_prop:yes" parselock setprop
    tobj @ "_test_prop" tobj @ "{if:{testlock:%d,_thelock},yes,no}" fmtstring setprop
    "_test_prop:yes" parselock
    tobj @ swap testlock not and 

    if me @ "Test passed." notify then
;
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
