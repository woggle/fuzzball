#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestManipObject(MufProgramTestBase):
    def test_props(self):
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
