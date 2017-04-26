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
        self.test = self._test
    
    def _test(self):
        result = self._test_program(self.code, pass_check=False)
        for pattern in self.patterns:
            self.assertTrue(re.search(pattern, result),
                msg='expected output for %s: <%s> to match <%s>' % (self.filename, result, pattern))

def normalize_filename(name):
    name = re.sub(r'/muf-tests/', '', name)
    name = re.sub(r'/', '_', name)
    name = re.sub(r'\.muf', '', name)
    name = re.sub(r'\.', '', name)
    return name

def generate():
    for root, dirs, files in os.walk('./muf-tests'):
        for file in files:
            if file.endswith('.muf'):
                result = {}
                with open(os.path.join(root, file), 'rb') as fh:
                    code = fh.read()
                    expect_patterns = re.findall(rb'^EXPECT:(.*)', code, flags=re.MULTILINE)
                    before = re.findall(rb'^BEFORE:(.*)', code, flags=re.MULTILINE)
                    after = re.findall(rb'^AFTER:(.*)', code, flags=re.MULTILINE)
                    if len(expect_patterns) == 0:
                        expect_patterns = [rb'\nTest passed.']
                    result['before'] = b'\n'.join(before)
                    result['after'] = b'\n'.join(after)
                    result['patterns'] = expect_patterns
                    result['code'] = code
                result['filename'] = os.path.join(root, file)
                result['description'] = file
                # hide fixture from test discovery
                def _test(self):
                    result = self._test_program(self.code, pass_check=False, before=self.before, after=self.after)
                    for pattern in self.patterns:
                        self.assertTrue(re.search(pattern, result),
                            msg='expected output for %s: <%s> to match <%s>' % (self.filename, result, pattern))
                result['test'] = _test
                name = normalize_filename(result['filename'])
                globals()[name] = type(name, (ServerTestBase,), result)

generate()

class TestListener(ServerTestBase):
    def test_listen_room_muf(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
: main me @ swap "XXX" strcat notify ;
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
        self.assertTrue(b'One This is a message.XXX' in result)

        
    def test_listen_room_muf_dbrefprop(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
: main me @ swap "XXX" strcat notify ;
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
        self.assertTrue(b'One This is a message.XXX' in result)

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
