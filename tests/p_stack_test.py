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

    def test_popn_badarg(self):
        self._test_program(b"""
: main
    0 try -3 popn catch pop me @ "Test passed." notify endcatch
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

    def test_rotate4(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" "d" 4 rotate
    "a" strcmp not
    swap "d" strcmp not and
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

    def test_rotate_badarg(self):
        self._test_program(b"""
: main
    0 try 2 rotate catch
        pop me @ "Test passed." notify
    endcatch
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

    def test_lreverse(self):
        self._test_program(b"""
: main
    ":" "a" "b" "c" 3 lreverse
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

    def test_secure_sysvars(self):
        self._test_program(b"""
: main
    "foo" me ! "bar" loc ! "quux" trigger ! "other" command !
    secure_sysvars
    1
    "me" match me @ = and
    me @ location loc @ = and
    trig trigger @ = and
    command @ "other" strcmp and
    if me @ "Test passed." notify then
;
""")


class TestCheckArgs(MufProgramTestBase):
    ALL_TYPES = b"adDeEfFilpPrRsStTv?"
    def _make_expect_match(self, the_type, is_match=True):
        if is_match:
            return rb""" 0 try it @ "%s" checkargs pop 1 catch pop 0 endcatch and """ % (the_type)
        else:
            return rb""" 0 try it @ "%s" checkargs pop 1 catch pop 0 endcatch not and """ % (the_type)

    def _test_type(self, expr, match_types=''):
        all_things = b""
        for i in range(len(self.ALL_TYPES)):
            t = self.ALL_TYPES[i:i+1]
            all_things += self._make_expect_match(t, t in match_types or t == b'?') + b"\n"
        self._test_program(rb"""
: main
    %s var! it
    1
    %s
    if me @ "Test passed." notify then
;
""" % (expr, all_things))


    def test_func_address(self):
        self._test_type(rb"'main", match_types=b'a')

    def test_dbref_nothing(self):
        self._test_type(rb"#-1", match_types=b'defprt')

    def test_dbref_ambiguous(self):
        self._test_type(rb"#-2", match_types=b'defprt')

    def test_dbref_home(self):
        self._test_type(rb"#-3", match_types=b'dDrR')

    def test_room_zero(self):
        self._test_type(rb"#0", match_types=b'dDrR')

    def test_god(self):
        self._test_type(rb"#1", match_types=b'dDpP')

    def test_newexit(self):
        self._test_type(rb"""#0 "somename" newexit """, match_types=b'dDeE')

    def test_newobject(self):
        self._test_type(rb"""#0 "somename" newobject""", match_types=b'dDtT')

    def test_prog(self):
        self._test_type(rb"prog", match_types=b'dDfF')

    def test_integer(self):
        self._test_type(rb"42", match_types=b'i')

    def test_empty_string(self):
        self._test_type(rb""" "" """, match_types=b's')

    def test_string(self):
        self._test_type(rb""" "test" """, match_types=b'sS')

    def test_global_var(self):
        self._test_type(rb""" me """, match_types=b'v')

    def test_local_var(self):
        self._test_type(rb""" 1 localvar """, match_types=b'v')

    def test_scoped_var(self):
        self._test_type(rb""" var foo foo """, match_types=b'v')

    def test_lock(self):
        self._test_type(rb""" "me" parselock """, match_types=b'l')

    def test_garbage(self):
        self._test_type(rb""" #0 "Foo" newobject dup recycle """, match_types=b'd')

    def test_multiple(self):
        self._test_program(rb"""
: main
    1
    "foo" "bar" "baz" "s3" checkargs pop pop pop
    "foo" "bar" "baz" 3 "{s}" checkargs pop pop pop
    "foo" 42 "baz" 3 "sisi" checkargs pop pop pop pop
    0 "{ss}" checkargs pop
    #-1 "foo" "bar" 1 "{ss}" checkargs pop pop pop pop
    #-1 "quux" "baz" "foo" "bar" 2 "{ss}" checkargs pop pop pop pop pop pop
    0 try "foo" "bar" "baz" "s4" checkargs pop pop pop 0 and catch pop 1 endcatch and
    0 try 1 "foo" "bar" "s3" checkargs pop pop pop pop 0 and catch pop 1 endcatch and
    0 try 42 "bar" "baz" 3 "{s}" checkargs pop pop pop pop 0 and catch pop 1 endcatch and
    0 try 42 "bar" "baz" 3 "iss" checkargs pop pop pop pop 0 and catch pop 1 endcatch and
    0 try #-1 "bar" "foo" "bar" 2 "{ss}" checkargs pop pop pop pop pop 0 and catch pop 1 endcatch and
    if me @ "Test passed." notify then
;
""")

    def test_underflow(self):
        self._test_program(rb"""
: main
    begin fulldepth while pop repeat
    1 var! successp
    0 try "foo" "bar" "baz" "s4" checkargs 0 successp ! catch pop endcatch
    0 try 4 "{s}" checkargs 0 successp ! catch pop endcatch
    0 try 3 4 "foo" "{i}s" checkargs 0 successp ! catch pop endcatch
    successp @ if me @ "Test passed." notify then
;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
