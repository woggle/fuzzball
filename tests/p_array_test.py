#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestArrayFlat(MufProgramTestBase):
    def test_simple_get(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  dup 0 array_getitem 1 = 
  over 1 array_getitem "two" strcmp not and
  over 2 array_getitem 3.0 = and
  over array_count 6 = and
  over array_last swap 5 = and and
  over array_first swap 0 = and and
  over 3 array_next 1 = swap 4 = and and
  over 3 array_prev 1 = swap 2 = and and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_getrange(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  1 3 array_getrange
  { "two" 3.0 4 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_insertrange(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  2 { "foo" "bar" }list array_insertrange
  { 1 "two" "foo" "bar" 3.0 4 5 6 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")
    
    def test_setrange(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  2 { "foo" "bar" }list array_setrange
  { 1 "two" "foo" "bar" 5 6 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_delrange(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  2 3  array_delrange
  { 1 "two" 5 6 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_cut(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  3  array_cut
  swap
  { 1 "two" 3.0 }list array_compare 0 =
  swap
  { 4 5 6 }list array_compare 0 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")
    
    def test_simple_set_append(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  "new two" swap 1 array_setitem
  "new value" swap array_appenditem
  3 array_delitem
  dup 0 array_getitem 1 = 
  over 1 array_getitem "new two" strcmp not and
  over 2 array_getitem 3.0 = and
  over 3 array_getitem 5 = and
  over 5 array_getitem "new value" strcmp not and
  over array_count 6 = and
  over array_last swap 5 = and and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")
    def test_explode(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  array_explode
  6 =
  swap 6 = and
  swap 5 = and
  swap 5 = and
  swap 4 = and
  swap 4 = and
  swap 3 = and
  swap 3.0 = and
  swap 2 = and
  swap "two" strcmp not and
  swap 1 = and
  swap 1 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_vals(self):
        self._test_program(b"""
: main
  { 1 "two" 3.5 4 5 6 }list
  array_vals
  6 =
  swap 6 = and
  swap 5 = and
  swap 4 = and
  swap 3.5 = and
  swap "two" strcmp not and
  swap 1 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_keys(self):
        self._test_program(b"""
: main
  { 1 "two" 3.0 4 5 6 }list
  array_keys
  6 =
  swap 5 = and
  swap 4 = and
  swap 3 = and
  swap 2 = and
  swap 1 = and
  swap 0 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")
    
    def test_insert(self):
        self._test_program(b"""
: main
  "new two"
  { 1 "two" 3.0 4 5 6 }list
  1
  array_insertitem
  dup 1 array_getitem "new two" strcmp not
  swap 2 array_getitem "two" strcmp not and
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
  { 1 "two" 3.0 4 5 6 }list
  array_reverse
  dup 1 array_getitem 5 = 
  swap 4 array_getitem "two" strcmp not and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
""")

    def test_sort_simple(self):
        self._test_program(b"""
: main
    { 6 3 5 9 3 }list
    0 array_sort
    array_vals
    5 =
    swap 9 = and
    swap 6 = and
    swap 5 = and
    swap 3 = and
    swap 3 = and
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_shuffle(self):
        self._test_program(b"""
: main
    { 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 }list
    dup
    4 array_sort
    0 array_sort
    array_compare 0 = 
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")
    
    def test_array_notify(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
: main
    { "This is the first line." "This is the second line." }list
    { me @ }list array_notify
;
.
c
q
@set test.muf=D
@act runtest=me
@link runtest=test.muf
runtest
""")
        self.assertTrue(b'\nThis is the first line.' in result)
        self.assertTrue(b'\nThis is the second line.' in result)

    def test_array_join(self):
        self._test_program(b"""
: main
    { 1 #2 3.0 "test" }list ":" array_join
    "1:#2:3.0:test" strcmp not if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_interpret(self):
        self._test_program(b"""
: main
    { 1 #0 3.0 "test" }list array_interpret
    "1Room Zero3.0test" strcmp not if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_union(self):
        self._test_program(b"""
: main
    { 1 2 3 "test" #1 }list
    { 3 4 5 "test" "test2" #2 }list
    { "other" }list
    3 array_nunion
    0 array_sort
    { 1 2 3 4 5 "test" "test2" "other" #1 #2 }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_intersection_empty(self):
        self._test_program(b"""
: main
    { 1 2 3 "test" #1 }list
    { 3 4 5 "test" "test2" #2 }list
    { "other" }list
    3 array_nintersect
    array_count 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")
    
    def test_array_intersection(self):
        self._test_program(b"""
: main
    { 1 2 3 "test" "test2" #1 #2 }list
    { 3 4 5 "test" "test2" #2 }list
    { #2 "other" "test2" }list
    3 array_nintersect
    0 array_sort
    { "test2" #2 }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_difference(self):
        self._test_program(b"""
: main
    { 3 4 5 "test" "test2" #2 }list
    { #2 "other" "test2" }list
    { 1 2 3 "test" #1 }list
    3 array_ndiff
    0 array_sort
    { 1 2 #1 }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")
    
    def test_array_sort_indexed(self):
        self._test_program(b"""
: main
    {
        { "name" "One"     "num" 1 }dict
        { "name" "Two"     "num" 2 }dict
        { "name" "Three"   "num" 3 }dict
    }list
    SORTTYPE_DESCENDING "num" ARRAY_SORT_INDEXED
    {
        { "name" "Three"   "num" 3 }dict
        { "name" "Two"     "num" 2 }dict
        { "name" "One"     "num" 1 }dict
    }list
    array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_findval_simple(self):
        # documentation example
        self._test_program(b"""
: main
    { #5 #10 #15 #10 #20 }list #10 array_findval  
    { 1 3 }list array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_compare_simple(self):
        self._test_program(b"""
: main
    { #5 #10 #15 #10 #20 }list 
    { #5 #10 #16 #10 #20 }list array_compare
    0 <
    { #5 #10 #15 #10 #21 }list 
    { #5 #10 #15 #10 #20 }list array_compare
    0 > and
    { #5 "#1&#2" parselock }list 
    { #5 "#1|#2" parselock }list array_compare
    0 != and
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")



    def test_array_excludeval(self):
        self._test_program(b"""
: main
    { #5 #10 #15 #10 #20 }list #10 array_excludeval
    { 0 2 4 }list array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

class TestArrayFilterFlags(MufProgramTestBase):
    
    def test_simple(self):
        self._test_program(b"""
: main
    { #0 #1 #2 #3 #4 #5 }list "PW" array_filter_flags { #1 }list array_compare 0 =
    { #0 #1 #2 #3 #4 #5 }list "P!W" array_filter_flags { #4 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "P" array_filter_flags { #1 #4 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "R" array_filter_flags { #0 }list array_compare 0 = and
    { #0 #1 #2 #3 #4 #5 }list "!T" array_filter_flags { #0 #1 #2 #3 #4 }list array_compare 0 = and
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""", before=b"""
@pcreate IdFour=test
@create IdFive
""")

class TestArrayProps(MufProgramTestBase):
    def test_array_get_propdirs_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_get_propdirs_wizprops(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test/@doublesecret/foo" 3 setprop
    dup "_test/~unsecret/foo" 4 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" "@doublesecret" "~unsecret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""",before=b"@set test.muf=W")

    def test_array_get_propdirs_wizprops_unreadable(self):
        self._test_program(b"""
: main
    #2
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""",before=b"""
@create Foo
@set Foo=_test/@doublesecret:foo
@set Foo=_test/@doublesecret/bar:quux
""")



class TestArrayDict(MufProgramTestBase):
    def test_array_get_propvals_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_test/_bar" 1 setprop
    dup "_test/quux" #2 setprop
    dup "_test/xyxxy" "stuff" setprop
    dup "_test/.secret" "#1&#0" parselock setprop
    dup "_test/.verysecret" 2.0 setprop
    dup "_test" array_get_propvals
    {
            "_bar" 1 
            "quux" #2
            "xyxxy" "stuff"
            ".secret" "#1&#0" parselock
            ".verysecret" 2.0
    }dict
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")
   
    # FIXME: test permission denied 
    def test_array_get_proplist_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_test#/1" 1 setprop
    dup "_test#/2" #2 setprop
    dup "_test#/3" "stuff" setprop
    dup "_test#/4" "#1&#0" parselock setprop
    dup "_test#/5" 2.0 setprop
    dup "_test#" 5 setprop
    dup "_test" array_get_proplist
    {
            1
            #2
            "stuff"
            "#1&#0" parselock
            2.0
    }list
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")
    
    # FIXME: test permission denied
    def test_array_put_propvals_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_testdir"
    {
            "first" 1 
            "second" #2
            "third" "stuff"
            "fourth" "#1&#0" parselock
            "fifth" 2.0
    }dict
    array_put_propvals
    dup "_testdir/first" getprop 1 = 
    over "_testdir/second" getprop dup dbref? swap #2 = and and
    over "_testdir/third" getprop "stuff" strcmp not and
    over "_testdir/fourth" getprop unparselock "#1&#0" parselock unparselock strcmp not and
    over "_testdir/fifth" getprop 2.0 = and
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_put_proplist_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_testdir"
    {
            1 
            #2
            "stuff"
            "#1&#0" parselock
            2.0
    }list
    array_put_proplist
    dup "_testdir#/1" getprop 1 = 
    over "_testdir#/2" getprop dup dbref? swap #2 = and and
    over "_testdir#/3" getprop "stuff" strcmp not and
    over "_testdir#/4" getprop unparselock "#1&#0" parselock unparselock strcmp not and
    over "_testdir#/5" getprop 2.0 = and
    over "_testdir#" getprop 5 = and
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_get_reflist_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_testprop" "#1234 #5678 #2356" setprop
    dup "_testprop" array_get_reflist
    { #1234 #5678 #2356 }list array_compare 0 = 
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_put_reflist_simple(self):
        self._test_program(b"""
: main
    me @ "Foo" newobject
    dup "_testprop" { #1234 #5678 #2356 }list array_put_reflist
    "_testprop" getprop "#1234 #5678 #2356" strcmp not
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
""")

    def test_array_extract_simple(self):
        self._test_program(b"""
: main
    { #5 #10 #15 #10 #20 }list 
    { 0 3 4 }list array_extract
    { 0 #5  3 #10  4 #20 }dict array_compare 0 =
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
