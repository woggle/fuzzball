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


class TestSplit(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foo::bar:baz::quux" "::" split
    "bar:baz::quux" strcmp not
    swap "foo" strcmp not and
    "foo:bar" "::" split
    "" strcmp not 
    swap "foo:bar" strcmp not and
    and
    if me @ "Test passed." notify then
;
""")


class TestRSplit(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foo::bar:baz::quux" "::" rsplit
    "quux" strcmp not 
    swap "foo::bar:baz" strcmp not and
    "foo:bar" "::" rsplit
    "" strcmp not 
    swap "foo:bar" strcmp not and
    and
    if me @ "Test passed." notify then
;
""")

class TestCToI(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "" ctoi 0 =
    "a" ctoi 97 = and
    if me @ "Test passed." notify then
;
""")

class TestIToC(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1 itoc not
    97 itoc "a" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestSToD(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "" stod #-1 =
    "bad" stod #-1 = and
    "42" stod #42 =  and
    "#42" stod #42 = and
    "#-17" stod #-17 = and
    if me @ "Test passed." notify then
;
""")

class TestMidStr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foobarbaz" 4 4 midstr "barb" strcmp not 
    "foobarbaz" 17 3 midstr "" strcmp not and
    "foobarbaz" 7 4 midstr "baz" strcmp not and
    "" 4 6 midstr "" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestNumberP(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "42" number? and
    "foo" number? not and
    "123foo" number? not and
    "" number? not and
    if me @ "Test passed." notify then
;
""")

class TestStringCmp(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "abc" "AbC" stringcmp not and
    "abc" "abc " stringcmp 0 < and
    "abc " "abc" stringcmp 0 > and
    "cde" "abcde" stringcmp 0 > and
    "" "foo" stringcmp 0 < and
    "foo" "" stringcmp 0 > and
    "" "" stringcmp not and
    if me @ "Test passed." notify then
;
""")

class TestStrCmp(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "abc" "AbC" strcmp 0 > and
    "abc" "abc " strcmp 0 < and
    "abc " "abc" strcmp 0 > and
    "cde" "abcde" strcmp 0 > and
    "" "foo" strcmp 0 < and
    "foo" "" strcmp 0 > and
    "" "" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestStrNCmp(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "abc" "AbC" 3 strncmp 0 > and
    "abc" "AbC" 4 strncmp 0 > and
    "abc" "AbC" 2 strncmp 0 > and
    "abc" "abc " 4 strncmp 0 < and
    "abc" "abc " 5 strncmp 0 < and
    "abc" "abc " 3 strncmp 0 = and
    "abc " "abc" 4 strncmp 0 > and
    "abc " "abc" 3 strncmp 0 = and
    "abc " "abc" 2 strncmp 0 = and
    "cde" "abcde" 1 strncmp 0 > and
    "cde" "abcde" 10 strncmp 0 > and
    "cde" "abcde" 0 strncmp 0 = and
    "" "foo" 1 strncmp 0 < and
    "foo" "" 1 strncmp 0 > and
    "" "" 1 strncmp not and
    if me @ "Test passed." notify then
;
""")

class TestStrCut(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" 0 strcut "" strcmp not swap "" strcmp not and and
    "foobar" 3 strcut "bar" strcmp not swap "foo" strcmp not and and
    "foo" 3 strcut "" strcmp not swap "foo" strcmp not and and
    "foo" 4 strcut "" strcmp not swap "foo" strcmp not and and
    "foobar" 0 strcut "foobar" strcmp not swap "" strcmp not and and
    if me @ "Test passed." notify then
;
""")

class TestStrLen(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" strlen 0 = and
    "foo" strlen 3 = and
    if me @ "Test passed." notify then
;
""")

class TestStrCat(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "This " "is a test" strcat "This is a test" strcmp not and
    "This " "" strcat "This " strcmp not and
    "" "This " strcat "This " strcmp not and
    "" "" strcat "" strcmp not and
    if me @ "Test passed." notify then
;
""")
    
    def test_overflow(self):
        self._test_program(b"""
: main
    0 try
        "" begin
            "more" strcat
        repeat
    catch "overflow" instring if me @ "Test passed." notify then endcatch
;
""")


class TestAToI(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" atoi 0 = and
    "1" atoi 1 = and
    "123foo" atoi 123 = and
    "bar" atoi 0 = and
    if me @ "Test passed." notify then
;
""")

class TestNotify(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    me @ "Test passed." notify
;
""")

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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
