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

class TestIntoStr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
lvar localVarNumberZero
: main
    1
    1 intostr "1" strcmp not and
    #1 intostr "1" strcmp not and
    1.0 intostr strtof 1.0 = and
    me intostr "0" strcmp not and
    localVarNumberZero intostr "0" strcmp not and
    { }list 1 try intostr pop 0 and catch pop 1 and endcatch
    if me @ "Test passed." notify then
;
""")
    
class TestExplode(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foo::::bar::baz::quux" "::" explode
    array_make
    { "quux" "baz" "bar" "" "foo" }list
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")

class TestExplodeArray(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foo::::bar::baz::quux" "::" explode_array
    { "foo" "" "bar" "baz" "quux" }list
    array_compare 0 =
    if me @ "Test passed." notify then
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


class TestSubst(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    "foobarbazbarbaz" "quux" "bar" subst
    "fooquuxbazquuxbaz" strcmp not 
    if me @ "Test passed." notify then
;
""")
    
    def test_overflow_one(self):
        self._test_program(b"""
: main
    0 try
        "foobar" begin "barquux" "bar" subst repeat
    catch "overflow" instring if me @ "Test passed." notify then endcatch
;
""")

    def test_overflow_two(self):
        self._test_program(b"""
: main
    0 try
        "foobar" begin "quuxbar" "bar" subst repeat
    catch "overflow" instring if me @ "Test passed." notify then endcatch
;
""")


class TestInstr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" "x" instr not and
    "foobarbazbar" "bar" instr 4 = and
    "barfoobar" "bar" instr 1 = and
    "barfoobazbar" "quux" instr not and
    "foo" "foo" instr 1 = and
    if me @ "Test passed." notify then
;
""")

class TestRInstr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" "x" rinstr not and
    "foobarbazbar" "bar" rinstr 10 = and
    "barfoobar" "bar" rinstr 7 = and
    "barfoobazbar" "quux" rinstr not and
    "bar" "bar" rinstr 1 = and
    "xxxbar" "bar" rinstr 4 = and
    if me @ "Test passed." notify then
;
""")

class TestInstring(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" "x" instring not and
    "fOobArbazbar" "bar" instring 4 = and
    "baRfooBAr" "BAR" instring 1 = and
    "barFoobazbar" "quux" instring not and
    "FoO" "fOo" instring 1 = and
    if me @ "Test passed." notify then
;
""")

class TestRInstring(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1
    "" "x" rinstring not and
    "foobaRbazbAR" "bar" rinstring 10 = and
    "barfooBAr" "bAR" rinstring 7 = and
    "barfoobazbAr" "quux" rinstring not and
    "bar" "BAR" rinstring 1 = and
    "xxxbAr" "Bar" rinstring 4 = and
    if me @ "Test passed." notify then
;
""")

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

    # FIXME test breaks because %x:%N... does something bad
    @unittest.skip("known bugs here")
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


class TestToUpper(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1 
    "" toupper "" strcmp not and
    "foo" toupper "FOO" strcmp not and
    "fOo123bar" toupper "FOO123BAR" strcmp not and 
    if me @ "Test passed." notify then
;
""")

class TestToLower(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1 
    "" tolower "" strcmp not and
    "FOO" tolower "foo" strcmp not and
    "FOo123BaR" tolower "foo123bar" strcmp not and 
    if me @ "Test passed." notify then
;
""")

class TestUnparseObj(MufProgramTestBase):
    def test_simple(self):
        self._test_program(b"""
: main
    1 
    #1 unparseobj "One(#1PWM3)" strcmp not and

    #0 "Test Object" newobject
    dup "V" set 
    dup "Z" set
    unparseobj
    "Test Object(#4VZ)" strcmp not and

    #-1 unparseobj "*NOTHING*" strcmp not and

    #400 unparseobj "*INVALID*" strcmp not and
    
    #-4 unparseobj "*NIL*" strcmp not and

    #-3 unparseobj "*HOME*" strcmp not and

    if me @ "Test passed." notify then
;
""")

class TestSMatch(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" "" smatch and
    "foobar" "FOOBAR" smatch and
    "foobar" "foobaz" smatch not and
    "foobar" "*b?r" smatch and
    "foobar" "*b?z" smatch not and
    "foobar" "{foo}bar" smatch not and
    "foo bar" "{foo|baz} bar" smatch and
    "baz bar" "{foo|baz} bar" smatch and
    "foo bar" "{foo}*" smatch and
    "foobar" "{foo}*" smatch not and
    "foobarbaz" "[a-g]oo*" smatch and
    "foobarbaz" "[^e]oo*" smatch and
    "foobarbaz" "[^f]oo*" smatch not and
    "^foo{bar}" "\\^foo?bar\\}" smatch and
    if me @ "Test passed." notify then
;
""")

class TestStripLead(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" striplead "" strcmp not and
    "  \rfoo  " striplead "foo  " strcmp not and
    "           bar" striplead "bar" strcmp not and
    "x" striplead "x" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestStripTail(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" striptail "" strcmp not and
    "  foo  \r \r  " striptail "  foo" strcmp not and
    "bar        \r    " striptail "bar" strcmp not and
    "x" striptail "x" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestStringPfx(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" "" stringpfx and
    "foo" "foo" stringpfx and
    "foobar" "foo" stringpfx and
    "foobar" "FOO" stringpfx and
    "" "foo" stringpfx not and
    "foo" "foobar" stringpfx not and
    "foo" "fou" stringpfx not and
    "foobar" "fou" stringpfx not and
    if me @ "Test passed." notify then
;
""")

class TestAttr(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "foo" "reset" textattr "\[[0mfoo\[[0m" strcmp not and
    "foo" "normal" textattr "\[[0mfoo\[[0m" strcmp not and
    "foo" "red,bg_black,reverse" textattr "\[[31m\[[40m\[[7mfoo\[[0m" strcmp not and
    "foo" "black,bg_red,bold" textattr "\[[30m\[[41m\[[1mfoo\[[0m" strcmp not and
    "foo" "green,bg_green,dim" textattr "\[[32m\[[42m\[[2mfoo\[[0m" strcmp not and
    "foo" "yellow,bg_yellow,italic" textattr "\[[33m\[[43m\[[3mfoo\[[0m" strcmp not and
    "foo" "blue,bg_blue,underline" textattr "\[[34m\[[44m\[[4mfoo\[[0m" strcmp not and
    "foo" "magenta,bg_magenta,ostrike" textattr "\[[35m\[[45m\[[9mfoo\[[0m" strcmp not and
    "foo" "cyan,bg_cyan,flash" textattr "\[[36m\[[46m\[[5mfoo\[[0m" strcmp not and
    "foo" "white,bg_white,overstrike" textattr "\[[37m\[[47m\[[9mfoo\[[0m" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestTokenSplit(MufProgramTestBase):
    def test_doc_example(self):
        self._test_program(rb"""
: main
    1
    "ab//cd/'efg'hi//jk'lm"   "'"   "/"   TOKENSPLIT
    3 array_make
    "ab/cd'efg"   "hi//jk'lm"   "'"
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_doc_example_otherdelim(self):
        self._test_program(rb"""
: main
    1
    "ab//cd/'efg'hi//jk'lm"   ":'"   "/"   TOKENSPLIT
    3 array_make
    "ab/cd'efg"   "hi//jk'lm"   "'"
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_end(self):
        self._test_program(rb"""
: main
    1
    "foo/bar"   "'"   "/"   TOKENSPLIT
    3 array_make
    "foobar"   ""   ""
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")
    
    def test_empty(self):
        self._test_program(rb"""
: main
    1
    ""   ":"   ""   TOKENSPLIT
    3 array_make
    ""   ""   ""
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_esc_is_del(self):
        self._test_program(rb"""
: main
    1
    "foo//bar/baz/quux"   "/"   "/x"   TOKENSPLIT
    3 array_make
    "foo/bar"   "baz/quux"   "/"
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
""")

class TestAnsiStrlen(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" ansi_strlen 0 = and
    "foobar" ansi_strlen 6 = and
    "\[[0mfoo\[[3;03mbar\[[0m" ansi_strlen 6 = and
    if me @ "Test passed." notify then
;
""")

class TestAnsiStrcut(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" 0 ansi_strcut "" strcmp not swap "" strcmp not and and
    "foobar" 3 ansi_strcut "bar" strcmp not swap "foo" strcmp not and and
    "foobar" 6 ansi_strcut "" strcmp not swap "foobar" strcmp not and and
    "foobar" 7 ansi_strcut "" strcmp not swap "foobar" strcmp not and and
    "foobar" 0 ansi_strcut "foobar" strcmp not swap "" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 ansi_strcut
        "\[[0m" strcmp not 
        swap "\[[0mfoo\[[3;03mbar" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 7 ansi_strcut
        "" strcmp not 
        swap "\[[0mfoo\[[3;03mbar\[[0m" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 2 ansi_strcut
        "o\[[3;03mbar\[[0m" strcmp not 
        swap "\[[0mfo" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 3 ansi_strcut
        "\[[3;03mbar\[[0m" strcmp not 
        swap "\[[0mfoo" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 0 ansi_strcut
        "\[[0mfoo\[[3;03mbar\[[0m" strcmp not 
        swap "" strcmp not  and and
    if me @ "Test passed." notify then
;
""")

class TestAnsiStrip(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" ansi_strip "" strcmp not and
    "foobar" ansi_strip "foobar" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" ansi_strip "foobar" strcmp not and
    "\[[00000foobarquux" ansi_strip "foobarquux" strcmp not and
    "stuff\[[35;45mstuff" ansi_strip "stuffstuff" strcmp not and
    if me @ "Test passed." notify then
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

class TestMD5(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" md5hash "d41d8cd98f00b204e9800998ecf8427e" strcmp not and
    "test" md5hash "098f6bcd4621d373cade4e832627b4f6" strcmp not and
    "test\r" md5hash "1fd94de8c776d546d46902d35a437fe2" strcmp not and
    if me @ "Test passed." notify then
;
""")

class TestSHA1(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "" sha1hash "da39a3ee5e6b4b0d3255bfef95601890afd80709" strcmp not and
    "test" sha1hash "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3" strcmp not and
    "test\r" sha1hash "923f760def6227e59cf25c6feaef8a2598a5de97" strcmp not and
    if me @ "Test passed." notify then
;
""")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
