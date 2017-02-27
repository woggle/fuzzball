#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class MufProgramTestBase(ServerTestBase):
    def _test_program(self,program):
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
runtest
QUIT
""")
        self.assertTrue(b'\nTest passed.' in result)


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
QUIT
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
QUIT
""")
        # Either in @ps output or directly
        self.assertTrue(b'One This is a message.' in result)

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
    array_notify
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



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
