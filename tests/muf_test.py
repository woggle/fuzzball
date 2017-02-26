#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

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

class TestArrayFlat(ServerTestBase):
    def test_simple_get(self):
        result = self._do_full_session(CONNECT +
b"""
@program test.muf
i
: main
  { 1 "two" 3.0 4 5 6 }list
  dup 0 array_getitem 1 = 
  over 1 array_getitem "two" strcmp not and
  over 2 array_getitem 3.0 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
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
        self.assertTrue(b'\nTest passed.' in result)
    
    def test_simple_set_append(self):
        result = self._do_full_session(CONNECT +
b"""
@program test.muf
i
: main
  { 1 "two" 3.0 4 5 6 }list
  "new two" swap 1 array_setitem
  "new value" swap array_appenditem
  dup 0 array_getitem 1 = 
  over 1 array_getitem "new two" strcmp not and
  over 2 array_getitem 3.0 = and
  over 6 array_getitem "new value" strcmp not and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
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
        self.assertTrue(b'\nTest passed.' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
