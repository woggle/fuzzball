#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestListener(ServerTestBase):
    def test_listen_room_muf(self):
        result = self._do_full_session(CONNECT_GOD +
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
        result = self._do_full_session(CONNECT_GOD +
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

class TestTry(MufProgramTestBase):
    def test_simple_try(self):
        result = self._test_program(b"""
: main
    "original value"
    "bar" { "foo" "more foo" }list "baz" 3 try "xxx" abort
    catch "xxx" instring over "original value" strcmp not and if me @ "Test passed." notify then endcatch
    

;
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
