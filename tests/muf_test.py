#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class MufProgramTestBase(ServerTestBase):
    def _test_program(self, program, before=b"", after=b""):
        result = self._do_full_session(CONNECT +
b"""
@program test.muf
i
""" + program + b"""
.
c
q
@set test.muf=D
@act runtest=me
@link runtest=test.muf
""" + before + b"""
runtest
""" + after + b"""
""")
        self.assertTrue(b'\nTest passed.' in result)
        return result


class TestListener(ServerTestBase):
    def test_listen_room_muf(self):
        result = self._do_full_session(CONNECT +
b"""
@program test.muf
i
: main me @ notify ;
.
c
q
@set here=_listen/act:2
@act test=here
@link test=here
@lock test=me&!me
@ofail test=This is a message.
@fail test=Your message.
test
@ps
""")
        # Either in @ps output or directly
        self.assertTrue(b'One This is a message.' in result)
        
    def test_listen_room_muf_dbrefprop(self):
        result = self._do_full_session(CONNECT +
b"""
@program test.muf
i
: main me @ notify ;
.
c
q
@propset here=dbref:_listen/act:test.muf
@act test=here
@link test=here
@lock test=me&!me
@ofail test=This is a message.
@fail test=Your message.
test
@ps
""")
        # Either in @ps output or directly
        self.assertTrue(b'One This is a message.' in result)

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
        result = self._do_full_session(CONNECT +
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
QUIT
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

class TestManipObject(MufProgramTestBase):
    def test_create(self):
        result = self._test_program(b"""
: main
    #0 "FooBar" newobject
    dup #4 = ( #2 is test.muf; #3 is action to run)
    over thing? and
    over location #0 = and
    over owner #1 = and
    over #1 swap controls and
    over pennies 1 = and
    if me @ "Test passed." notify then
;
""", after=b"\nex FooBar\n")
        self.assertTrue(b'Type: THING' in result)

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

class TestRegexp(MufProgramTestBase):
    def test_regmatch_simple_true(self):
        result = self._test_program(b"""
: main
    "THIS is a test!" "is(.*)test" 0 regexp
    1
    over array_count 2 = and
    over 0 array_getitem { 6 9 }list array_compare 0 = and
    over 1 array_getitem { 8 3 }list array_compare 0 = and
    swap pop
    over array_count 2 = and
    over 0 array_getitem "is a test" strcmp not and
    over 1 array_getitem " a " strcmp not and
    swap pop
    if me @ "Test passed." notify then
;
""")

    def test_regsub_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "is(.*?)test" "X\\\\1Y" REG_ALL regsub
    "THIS X a Y! THIS X still a Y!" strcmp not 
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "THIS" regsplit
    { "" " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_noempty_simple(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "THIS" regsplit_noempty
    { " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_regsplit_nomatch(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "NEVER MATCHES" regsplit
    { "THIS is a test! THIS is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")
    def test_regsplit_capture(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "(TH.S)" regsplit
    { "" " is a test! " " is still a test!" }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")
    def test_regsplit_invalid(self):
        result = self._test_program(b"""
: main
    "THIS is a test! THIS is still a test!" "(TH.S" 
    2 try regsplit catch
        if me @ "Test passed." notify then
    endcatch
;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
