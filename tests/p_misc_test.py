#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestQueue(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    "FromQueue" strcmp not if
        trig #-1 =
        loc @ #-1 = and
        if
            me @ "Test passed." notify
        then
        prog "_finished" 1 setprop
    else
        #-1 loc !
        0 prog "FromQueue" queue
        dup 0 = if "no PID" abort then
        begin 
            0 sleep 
            prog "_finished" getprop 1 = not while
        repeat 
    then
    
;
""")

class TestKill(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    "FromQueue" strcmp not if
        prog "_started" 1 setprop
        me @ "FAILED" notify
        begin 0 sleep repeat
    else
        #-1 loc !
        preempt
        0 prog "FromQueue" queue 
        dup kill 1 =  
        swap kill 0 =
        and
        foreground
        0 sleep
        prog "_started" getprop 0 = 
        and if me @ "Test passed." notify then
    then
    
;
""")
        self.assertTrue(b'\nFAILED' not in result)

class TestFork(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    var parentpid pid parentpid !
    var childpid
    fork dup 0 = if
        me @ "_child_done" pid setprop
    else
        childpid !
        begin 0 sleep
            me @ "_child_done" getprop
            0 = while
        repeat
        me @ "_child_done" getprop
        childpid @ = if me @ "Test passed." notify then
    then
;
""")

class TestStats(MufProgramTestBase):
    def test_simple_all(self):
        self._test_program(rb"""
: main
    #-1 stats 7 array_make
    { 4 1 1 0 1 1 0 }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_simple_One(self):
        self._test_program(rb"""
: main
    #1 stats 7 array_make
    { 4 1 1 0 1 1 0 }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

class TestIsPidP(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    "FromQueue" strcmp not if exit then
    1
    pid ispid? and
    -1 ispid? not and
    1000000 ispid? not and
    120 prog "FromQueue" queue dup ispid? over kill pop swap ispid? not and and
    if me @ "Test passed." notify then
;
""")

class TestForce(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    "Foo" "pass" newplayer
    "say This is a test string." force
;
""", before=b"""
@set test.muf=W
""", pass_check=False)
        self.assertTrue(b'Foo says, "This is a test string."' in result)

    def test_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        "arg" strcmp not
        command @ "testcmd" strcmp not and
        force_level 0 > and
        forcedby prog = and 
        if #1 "Test passed." notify then
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd arg" force
    then
;
""", before=b"""
@set test.muf=W
""")

    def test_double_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        dup "first" strcmp not if
            me @ "testcmd second" force
        else
            "second" strcmp not
            command @ "testcmd" strcmp not and
            force_level 1 > and
            forcedby prog = and 
            forcedby_array { prog prog }list array_compare 0 = and
            if #1 "Test passed." notify then
        then
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd first" force
    then
;
""", before=b"""
@set test.muf=W
""")

    def test_over_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        0 try 
            me @ "testcmd" force
        catch
            "call loops" instring if #1 "Test passed." notify then
        endcatch
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd first" force
    then
;
""", before=b"""
@set test.muf=W
""")

class TestSysparm(MufProgramTestBase):
    extra_params = {
        'pennies': 'XXX',
        'cpennies': 'YYY',
    }

    def test_read_param_simple_array(self):
        self._test_program(rb"""
: main
    "pennies" sysparm_array foreach swap pop
        dup "name" [] "pennies" strcmp not if
            "value" [] "XXX" strcmp not and
            if me @ "Test passed." notify then
        then
    repeat
;
""")

    def test_read_param_simple_array_noforeach(self):
        self._test_program(rb"""
: main
    "pennies" sysparm_array 0 []
        dup "name" [] "pennies" strcmp not if
            "value" [] "XXX" strcmp not and
            if me @ "Test passed." notify then
        then
;
""")

    def test_read_param_simple_array_noread(self):
        self._test_program(rb"""
: main
    "pennies" sysparm_array 0 []
    if me @ "Test passed." notify then
;
""")

    def test_read_param_simple_array_reallynoread(self):
        self._test_program(rb"""
: main
    "pennies" sysparm_array
    if me @ "Test passed." notify then
;
""")
    
    def test_read_param_simple(self):
        self._test_program(rb"""
: main
    "pennies" sysparm "XXX" strcmp not
    if me @ "Test passed." notify then
;
""")

    def test_set_param_simple(self):
        self._test_program(rb"""
: main
    "pennies" "ZZZ" setsysparm 
    "pennies" sysparm "ZZZ" strcmp not
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
