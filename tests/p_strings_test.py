#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestNotify(MufProgramTestBase):
    def test_listener_player(self):
        result = self._test_program(b"""
: main
    me @ "DoListener" notify
    0 sleep
    begin
        me @ "_found_listen" getprop 0 = while
        0 sleep
    repeat
    me @ "Test passed." notify_nolisten
;
""", before=b"""
@program listener.muf
i
: main
    dup "DoListener" strcmp not if
        me @ "_found_listen" 1 setprop
    then
    "Test passed." instring if me @ "FAILED." notify_nolisten then
;
.
c
q
@set listener.muf=D
@propset me=dbref:_listen:listener.muf
""")
        self.assertTrue(b"FAILED" not in result)

    def test_nolistener_player(self):
        result = self._test_program(b"""
: main
    me @ "DoListener" notify_nolisten
    0 sleep
    me @ "_found_listen" getprop not if
        me @ "Test passed." notify_nolisten
    then
;
""", before=b"""
@program listener.muf
i
: main
    dup "DoListener" strcmp not if
        me @ "_found_listen" 1 setprop
        me @ "FAILED" notify_nolisten
    then
;
.
c
q
@set listener.muf=D
@propset me=dbref:_listen:listener.muf
""")
        self.assertTrue(b"FAILED" not in result)

class TestPronounSub(MufProgramTestBase):
    extra_params =  { 'gender_prop': '_genderthingy' }

    def test_simple(self):
        self._test_program(b"""
: main
    1
    #1 "_genderthingy" "female" setprop
    #1 "%N" "the One" setprop
    #1 "%N:%n:%a:%A:%s:%S:%o:%O:%p:%P:%r:%R:" pronoun_sub
    me @ over notify
    "The One:the One:hers:Hers:she:She:her:Her:her:Her:herself:Herself:" strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_props(self):
        self._test_program(b"""
: main
    1
    #0 "testObjectThingy" newobject
    dup "_genderthingy" "herm" setprop
    dup "%N" "testObjecty" setprop
    dup "%a" "alpha" setprop
    dup "%x" "stuff" setprop
    dup "_pronouns/herm/%p" "beta" setprop
    #0 "_pronouns/herm/%o" "delta" setprop
    #0 "_pronouns/herm/%r" "%N's omega" setprop
    "%N:%n:%a:%A:%s:%S:%o:%O:%p:%P:%r:%R:%x" pronoun_sub
    me @ over notify
    "TestObjecty:testObjecty:alpha:Alpha:sie:Sie:delta:Delta:beta:Beta:testObjectThingy's omega:TestObjectThingy's omega:stuff" strcmp not and
    if me @ "Test passed." notify then
;
""")

    # FIXME: should test MPI running from pronoun_sub

    def test_overflow(self):
        self._test_program(b"""
: main
    #1 "_genderthingy" "female" setprop
    1
    #1 "%N" "alonglonglonglonglonglonglonglonglonglonglonglonglongstring" setprop
    0 "" begin
        "%N" strcat #1 over pronoun_sub strlen
        rot over = not while
        swap
    repeat
    me @ "Test passed." notify
;
""")


class TestAnsiMidStr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" 1 0 ansi_midstr "" strcmp not and
    "foobar" 4 3 ansi_midstr "bar" strcmp not and
    "foobar" 4 4 ansi_midstr "bar" strcmp not and
    "foobar" 7 2 ansi_midstr "" strcmp not and
    "foobar" 8 2 ansi_midstr "" strcmp not and
    "foobar" 1 7 ansi_midstr "foobar" strcmp not and
    "foobar" 1 6 ansi_midstr "foobar" strcmp not and
    "foobar" 1 5 ansi_midstr "fooba" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 1 6 ansi_midstr
        "\[[0mfoo\[[3;03mbar" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 2 ansi_midstr
        "r\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 1 ansi_midstr
        "r" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 7 1 ansi_midstr
        "\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 1 7 ansi_midstr
        "\[[0mfoo\[[3;03mbar\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 3 3 ansi_midstr
        "o\[[3;03mba" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 4 4 ansi_midstr
        "\[[3;03mbar\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 4 0 ansi_midstr
        "" strcmp not and
    if me @ "Test passed." notify then
;
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
