#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestStringMath(MufProgramTestBase):
    extra_params = {'muf_string_math': 'yes'}
    
    def test_add(self):
        self._test_program(rb"""
: main
    1
    "foo" "bar" + "foobar" strcmp not and
    "" "" + "" strcmp not and
    "foo" "" + "foo" strcmp not and
    "" "bar" + "bar" strcmp not and
    if me @ "Test passed." notify then
;
""")
    
    def test_add_overflow(self):
        self._test_program(rb"""
: main
    1
    0 try
        "foo" 
        begin dup "bar" + swap over strcmp while repeat
    catch "overflow" instring if
        me @ "Test passed." notify
    then endcatch
;
""")

    def test_repeat_simple(self):
        self._test_program(rb"""
: main
    1
    "foo" 4 * "foofoofoofoo" strcmp not and
    "foo" 0 * "" strcmp not and
    "" 1000000000 * "" strcmp not and
    if
        me @ "Test passed." notify
    then
;
""")

    
    def test_repeat_overflow_simple(self):
        self._test_program(rb"""
: main
    1
    0 try
        "foo" 10000 *
    catch "overflow" instring if
        me @ "Test passed." notify
    then endcatch
;
""")

    def test_repeat_overflow_huge1(self):
        self._test_program(rb"""
: main
    1
    0 try
        "this is a long string" 102261127 *
    catch "overflow" instring if
        me @ "Test passed." notify
    then endcatch
;
""")

    def test_repeat_overflow_huge2(self):
        self._test_program(rb"""
: main
    1
    0 try
        "this is a long string" 102261126 *
    catch "overflow" instring if
        me @ "Test passed." notify
    then endcatch
;
""")

    def test_equal(self):
        self._test_program(rb"""
: main
    1
    "foo" "foo" = and
    "foo" "bar" = not and
    "foo" "" = not and
    "" "foo" = not and
    "" "" = and
    if me @ "Test passed." notify then
;
""")

class TestIntegerMath(MufProgramTestBase):
    extra_params = {'optimize_muf': 'no'}

    def test_addsubmultdivmod_simple(self):
        self._test_program(rb"""
: main
    1
    2 5 + 7 = and
    2 5 * 10 = and
    2 5 - -3 = and
    2 5 / 0 = and
    5 2 / 2 = and
    5 2 % 1 = and
    if me @ "Test passed." notify then
;
""")
   
    # This test assumes 32-bit int 
    # This test will fail because constnat folding
    # does not detect overflow correctly
    def test_addsubmultdivmod_overflow(self):
        if self.extra_params['optimize_muf'] == 'yes':
            self.skipTest('overflow detection broken with constant folding')
        self._test_program(rb"""
: main
    1
    clear
    2147483647 1 + 0 > err_ibounds? or and
    clear
    -2147483648 1 - 0 < err_ibounds? or and
    clear
    -2147483648 2 * 0 < err_ibounds? or and
    clear
    2147483647 2 * 0 > err_ibounds? or and
    clear
    -2147483648 -1 / 0 < err_ibounds? or and
    -2147483648 -1 % pop (result unspecified, but should not crash)
    if me @ "Test passed." notify then
;
""")

    def test_bitwise(self):
        self._test_program(rb"""
: main
    1
    2 5 bitor 7 = and
    2 2 bitor 2 = and
    2 5 bitxor 7 = and
    2 2 bitxor 0 = and
    2 5 bitand 0 = and
    2 2 bitand 2 = and
    2 6 bitand 2 = and
    2 3 bitshift 16 = and
    2 -3 bitshift 0 = and
    -1 1 bitshift -2 = and
    -1 -1 bitshift -1 = and
    4 0 bitshift 4 = and
    if me @ "Test passed." notify then
;
""")

    def test_comparison(self):
        self._test_program(rb"""
: main
    1
    2 5 > not and
    2 5 >= not and
    2 5 < and
    2 5 <= and
    2 -2147483648 > and
    2 -2147483648 >= and
    2 -2147483648 < not and
    2 -2147483648 <= not and
    2 2 = and
    2 5 = not and
    2 5 != and
    2 2 != not and
    if me @ "Test passed." notify then
;
""")

    def test_signabs(self):
        self._test_program(rb"""
: main
    1
    -2147483647 abs 2147483647 = and
    0 abs 0 = and
    2 abs 2 = and
    0 sign 0 = and
    -2147483648 sign -1 = and
    2 sign 1 = and
    if me @ "Test passed." notify then
;
""")

class TestIntegerMathInline(TestIntegerMath):
    extra_params = {'optimize_muf': 'yes'}


class TestLogic(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    1
    "foo" 0 and not and
    "foo" 0 or and
    "foo" 0 xor and
    if me @ "Test passed." notify then
;
""")


class TestRandom(MufProgramTestBase):
    def test_srand(self):
        self._test_program(rb"""
: main
    1
    "this is a string" setseed
    { srand srand srand srand }list
    "this is a string" setseed
    { srand srand srand srand }list
    array_compare 0 = and
    "this is a string" setseed
    srand srand pop pop
    getseed { srand srand }list
    swap setseed { srand srand }list
    array_compare 0 = and

    if me @ "Test passed." notify then
;
""")


class TestIncrDecr(MufProgramTestBase):
    def test_incrdecr_svar(self):
        self._test_program(rb"""
: main
    1
    0 var! test
    test ++
    test @ 1 = and
    test --
    test @ 0 = and
    #42 test !
    test ++
    test @ #43 = and
    test --
    test @ #42 = and
    42.0 test !
    test ++
    test @ 43.0 = and
    test --
    test @ 42.0 = and

    if me @ "Test passed." notify then
;
""")

    def test_incrdecr_constant(self):
        self._test_program(rb"""
: main
    1
    42 ++ 43 = and
    42 -- 41 = and
    #42 ++ #43 = and
    #42 -- #41 = and
    42.0 ++ 43.0 = and
    42.0 -- 41.0 = and

    if me @ "Test passed." notify then
;
""")

    def test_incrdecr_gvar(self):
        self._test_program(rb"""
var test
: main
    1
    0 test !
    test ++
    test @ 1 = and
    test --
    test @ 0 = and
    #42 test !
    test ++
    test @ #43 = and
    test --
    test @ #42 = and
    42.0 test !
    test ++
    test @ 43.0 = and
    test --
    test @ 42.0 = and

    if me @ "Test passed." notify then
;
""")

    def test_incrdecr_lvar(self):
        self._test_program(rb"""
lvar test
: main
    1
    0 test !
    test ++
    test @ 1 = and
    test --
    test @ 0 = and
    #42 test !
    test ++
    test @ #43 = and
    test --
    test @ #42 = and
    42.0 test !
    test ++
    test @ 43.0 = and
    test --
    test @ 42.0 = and

    if me @ "Test passed." notify then
;
""")


class TestInt(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
lvar test
: main
    1
    #42 int 42 = and
    42.2 int 42 = and
    -42.2 int -42 = and
    me int 0 = and
    test int 0 = and

    if me @ "Test passed." notify then
;
""")



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
