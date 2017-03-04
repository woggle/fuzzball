#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD


class TestFmtString(MufProgramTestBase):
    def test_int_format(self):
        self._test_program(b"""
: main
    1
    42 "%i" fmtstring "42" strcmp not and
    42 "%3i" fmtstring " 42" strcmp not and
    42 "%03i" fmtstring "042" strcmp not and
    42 "%-3i" fmtstring "42 " strcmp not and
    42 "%|4i" fmtstring " 42 " strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_str_format(self):
        self._test_program(b"""
: main
    1
    "ab" "%s" fmtstring "ab" strcmp not and
    "ab" "%3s" fmtstring " ab" strcmp not and
    "ab" "%-3s" fmtstring "ab " strcmp not and
    "ab" "%|4s" fmtstring " ab " strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_dbref_format(self):
        self._test_program(b"""
: main
    1
    #1 "%d" fmtstring "#1" strcmp not and
    #1 "%3d" fmtstring " #1" strcmp not and
    #1 "%-3d" fmtstring "#1 " strcmp not and
    #1 "%|4d" fmtstring " #1 " strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_dbref_format_name(self):
        self._test_program(b"""
: main
    1
    #1 "%D" fmtstring "One" strcmp not and
    #1 "%4D" fmtstring " One" strcmp not and
    #1 "%-4D" fmtstring "One " strcmp not and
    #1 "%|5D" fmtstring " One " strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_lock_format(self):
        self._test_program(b"""
: main
    1
    "me|!me" parselock "%l" fmtstring "me|!me" parselock prettylock strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_float_format(self):
        self._test_program(b"""
: main
    1
    42.0 "%f" fmtstring "42.000000" strcmp not and
    42.0 "%10f" fmtstring " 42.000000" strcmp not and
    42.0 "%.1f" fmtstring "42.0" strcmp not and
    42.0 "%5.1f" fmtstring " 42.0" strcmp not and
    42.0 "%|6.1f" fmtstring " 42.0 " strcmp not and
    42.0 "%03.0f" fmtstring "042" strcmp not and
    42.0 "%-3.0f" fmtstring "42 " strcmp not and
    42.0 "%|4.0f" fmtstring " 42 " strcmp not and
    pi "%4.2f" fmtstring "3.14" strcmp not and
    42.0 "%.1e" fmtstring "4.2e+01" strcmp not and
    42.0 "%.0e" fmtstring "4e+01" strcmp not and
    42.0 "%|7.0e" fmtstring " 4e+01 " strcmp not and
    42.0 "%|4.0e" fmtstring "4e+01" strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_escape(self):
        self._test_program(b"""
: main
    1
    "%%" fmtstring "%" strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_overflow_field_width(self):
        self._test_program(b"""
: main
    0 try
    "x"    dup   dup   dup   dup   dup   dup   dup   dup   dup   dup
    "%999s %999s %999s %999s %999s %999s %999s %999s %999s %999s %999s"
    fmtstring
    catch
        me @ "Test passed." notify
    endcatch
;
""")

    def test_overflow_strsize(self):
        self._test_program(b"""
: main
    "x" "%999s" fmtstring
    1 try
    dup    dup   dup   dup   dup   dup   dup   dup   dup   dup   dup
    "%s %s %s %s %s %s %s %s %s %s %s"
    fmtstring
    catch
        me @ "Test passed." notify
    endcatch
;
""")
    

class TestArrayFmtString(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    {
        {
            "a" 3.14
        }dict
    }list
    "%4.2[a]f" 
    array_fmtstrings { "3.14" }list array_compare 0 = if
        me @ "Test passed." notify
    then
;
""")

    def test_doc_example(self):
        self._test_program(b"""
: main
    {
        {
            "username" "Johnny"
            "count" 4
            "object" #18
            4  pi
        }dict
        {
            "username" "Ghaladahsk_Fadja"
            "count" 123
            "object" #97
            4 0.0
        }dict
    }list
    "%-16.15[username]s %3[count]i %5[object]d %4.2[4]f"
    array_fmtstrings
    dup 0 array_getitem me @ swap notify
    { 
    "Johnny             4   #18 3.14"
    "Ghaladahsk_Fadj  123   #97 0.00"
    }list array_compare 0 =
    if me @ "Test passed." notify then
;
""") 

    def test_overflow(self):
        self._test_program(b"""
: main
    {
        {
            "the_thing" "x"
        }dict
        {
            "the_thing" "x" "%999s" fmtstring
        }dict
    }list
    "%[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s "
    "%[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s" strcat
    2 try array_fmtstrings catch
        me @ "Test passed." notify
    endcatch
;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
