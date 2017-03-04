#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase


class TestStack(MufProgramTestBase):
    def test_pdup(self):
        self._test_program(b"""
: main
    "x" ?dup 0 ?dup 0 = swap "x" strcmp not and if
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")
    
    def test_popn(self):
        self._test_program(b"""
: main
    "a" "b" "c" "d" "e" "f" 3 popn
    "c" strcmp not
    swap "b" strcmp not and
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_dupn(self):
        self._test_program(b"""
: main
    "a" "b" "c" "d" "e" "f" 3 dupn
    "f" strcmp not
    swap "e" strcmp not and
    swap "d" strcmp not and
    swap "f" strcmp not and
    swap "e" strcmp not and
    swap "d" strcmp not and
    swap "c" strcmp not and
    swap "b" strcmp not and
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_ldup(self):
        self._test_program(b"""
: main
    "a" "b" "c" "d" "e" "f" 3 ldup
    3 = 
    swap "f" strcmp not and
    swap "e" strcmp not and
    swap "d" strcmp not and
    swap 3 = and
    swap "f" strcmp not and
    swap "e" strcmp not and
    swap "d" strcmp not and
    swap "c" strcmp not and
    swap "b" strcmp not and
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_nip(self):
        self._test_program(b"""
: main
    "a" "b" "c" nip
    "c" strcmp not
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_tuck(self):
        self._test_program(b"""
: main
    "a" "b" "c" tuck
    "c" strcmp not
    swap "b" strcmp not and
    swap "c" strcmp not and
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_put(self):
        self._test_program(b"""
: main
    "a" "b" "c" "x" 2 put
    "c" strcmp not 
    swap "x" strcmp not and
    swap "a" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_pick(self):
        self._test_program(b"""
: main
    "a" "b" "c" ":" ":" ":" 4 pick
    "c" strcmp not
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_rot(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" rot
    "a" strcmp not 
    swap "c" strcmp not and
    swap "b" strcmp not and
    swap ":" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_rrot(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" -rot
    "b" strcmp not 
    swap "a" strcmp not and
    swap "c" strcmp not and
    swap ":" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")
    
    def test_rotate(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" 3 rotate
    "a" strcmp not 
    swap "c" strcmp not and
    swap "b" strcmp not and
    swap ":" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")
    
    def test_depth(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" depth 5 = 
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_types(self):
        self._test_program(b"""
: main
    "a" string?
    42 int? and
    4.2 float? and
    { 0 }list array? and
    { "a" "b" }dict dictionary? and
    #1 dbref? and
    "me&!me" parselock lock? and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")
    
    def test_reverse(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" 3 reverse
    3 =
    swap "a" strcmp not and
    swap "b" strcmp not and
    swap "c" strcmp not and
    swap ":" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

    def test_reverse(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" 3 reverse
    "a" strcmp not 
    swap "b" strcmp not and
    swap "c" strcmp not and
    swap ":" strcmp not and
    if 
        me @ "Test passed." notify
    else
        me @ "Test failed." notify
    then
;
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
