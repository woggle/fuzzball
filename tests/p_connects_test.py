#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD


class TestOneConnection(MufProgramTestBase):
    def test_awake(self):
        self._test_program(rb"""
: main
    1
    me @ awake? and
    #0 "MyThing" newobject var! myobj
    myobj @ "Z" set
    myobj @ awake? and
    "FooBar" "password" newplayer awake? not and
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_online(self):
        self._test_program(rb"""
: main
    1
    online array_make
    { me @ }list array_compare 0 = and
    online_array
    { me @ }list array_compare 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_concount(self):
        self._test_program(rb"""
: main
    concount 1 = 
    if me @ "Test passed." notify then
;
""")

    def test_dbref(self):
        self._test_program(rb"""
: main
    1
    1 condbref #1 = and
    descr descrdbref #1 = and
    if me @ "Test passed." notify then
;
""")
    
    def test_idle_zero(self):
        self._test_program(rb"""
: main
    1
    1 conidle 0 = and
    descr descridle 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_time_zero(self):
        self._test_program(rb"""
: main
    1
    1 contime 0 = and
    descr descrtime 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_least_idle(self):
        self._test_program(rb"""
: main
    1
    #1 descrleastidle descr =
    "FooBar" "foo" newplayer
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_most_idle(self):
        self._test_program(rb"""
: main
    1
    #1 descrmostidle descr =
    if me @ "Test passed." notify then
;
""")

    def test_userhost_consistent(self):
        self._test_program(rb"""
: main
    1
    1 conhost descr descrhost strcmp not and 
    1 conuser descr descruser strcmp not and 
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

    def test_conboot_flush(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@program test.muf
1 i
: main 
    me @ "Before boot" notify
    1 condescr descrflush
    1 conboot 
    0 sleep
    me @ "FAILED!" notify
;
.
c
q
@set test.muf=D
@set test.muf=W
@act runtest=#0
@link runtest=test.muf
""")
        result = self._do_full_session(b"""
connect TestUser foo
runtest
here
""", autoquit=False)
        self.assertTrue(b'Before boot' in result)
        self.assertTrue(b'FAILED' not in result)

    def test_descrboot_flush(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@program test.muf
1 i
: main 
    me @ "Before boot" notify
    descr descrflush
    descr descrboot 
    0 sleep
    me @ "FAILED!" notify
;
.
c
q
@set test.muf=D
@set test.muf=W
@act runtest=#0
@link runtest=test.muf
""")
        result = self._do_full_session(b"""
connect TestUser foo
runtest
""", autoquit=False)
        self.assertTrue(b'Before boot' in result)
        self.assertTrue(b'FAILED' not in result)

    def test_condescr(self):
        self._test_program(rb"""
: main
    1
    1 condescr descr = and
    descr descrcon 1 = and 
    if me @ "Test passed." notify then
;
""")

    def test_connotify(self):
        self._test_program(rb"""
: main
    1 "Test passed." connotify
;
""")

    def test_descrnotify(self):
        self._test_program(rb"""
: main
    descr "Test passed." descrnotify
;
""")

    def test_firstlastnextdescr(self):
        self._test_program(rb"""
: main
    1
    descr nextdescr 0 = and
    99999 nextdescr 0 = and
    #1 firstdescr descr = and
    #1 lastdescr descr = and
    #-1 firstdescr descr = and
    #-1 lastdescr descr = and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_descriptors(self):
        self._test_program(rb"""
: main
    1
    #-1 descriptors array_make { descr }list array_compare 0 = and
    #1 descriptors array_make { descr }list array_compare 0 = and
    #-1 descr_array { descr }list array_compare 0 = and
    #1 descr_array { descr }list array_compare 0 = and
    "TestPlayer" "foo" newplayer var! thePlayer
    thePlayer @ descriptors array_make { }list array_compare 0 = and
    thePlayer @ descr_array { }list array_compare 0 = and
    if
        me @ "Test passed." notify
    then
;
""", before=rb"""
@set test.muf=W
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
