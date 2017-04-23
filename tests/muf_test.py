#!/usr/bin/env python3.6
import asyncio
import logging
import os
import os.path
import re
import unittest
import nose2

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class GenForMufFile(ServerTestBase):
    def __init__(self, the_file=None):
        super(ServerTestBase, self).__init__()
        self.filename = the_file
        with open(self.filename, 'rb') as fh:
            code = fh.read()
            expect_patterns = re.findall(rb'^EXPECT:(.*)', code)
            if len(expect_patterns) == 0:
                expect_patterns = [rb'\nTest passed.']
            self.patterns = expect_patterns
            self.code = code
        self.description = the_file
        # hide fixture from test discovery
        self.runTest = self._test

    def _test(self):
        result = self._test_program(code, pass_check=False)
        for pattern in expect_pattern:
            self.assertTrue(re.match(pattern, result),
                msg='expected output for %s: <%s> to match <%s>' % (self.filename, result, pattern))

def test_external_files():
    for root, dirs, files in os.walk('./muf-tests'):
        for file in files:
            if file.endswith('.muf'):
                yield (GenForMufFile(os.path.join(root, file)),)


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
    nose2.main()
