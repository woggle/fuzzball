#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestOpen(ServerTestBase):
    def test_one_link(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig Beta
@open foo;bar=#2=property
ex me=_reg/property
ex bar
""")
        self.assertTrue(b'Destination: Beta' in result)
        self.assertTrue(b'- ref /_reg/property:foo;bar(#3E' in result)

    def test_two(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@create IdThree
@open foo;bar=#2;#3=property
ex bar
""")
        self.assertTrue(b'Destination: IdTwo' in result)
        self.assertTrue(b'Destination: IdThree' in result)

class TestClone(ServerTestBase):
    extra_params = {'verbose_clone': 0}
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@create Foo
@desc Foo={null:to preserve}
@set Foo=@secretprop:42
@propset Foo=dbref:~protectedprop:#0
@propset Foo=lock:_lockprop:me
@set Foo=_proplist/a:foo
@set Foo=_proplist/b:bar
@clone Foo
""",
b"""
ex #3
ex #3=/
ex #3=_proplist/
""", use_dump=use_dump)
        self.assertTrue(b'Type: THING' in result)
        self.assertTrue(b'Foo(#3' in result)
        self.assertTrue(b'{null:to preserve}' in result)
        self.assertTrue(b'str /@secretprop:42' in result)
        self.assertTrue(b'ref /~protectedprop:Room Zero' in result)
        self.assertTrue(b'lok /_lockprop:One' in result)
        self.assertTrue(b'str /_proplist/a:foo' in result)
        self.assertTrue(b'str /_proplist/b:bar' in result)

    def test_dump(self):
        self._test(use_dump=True)
    
    def test_nodump(self):
        self._test(use_dump=False)

class TestAttach(ServerTestBase):
    def _test(self, use_dump=False):
        result = self._do_dump_test(
b"""
@act foo=me
@attach foo=#0
""",
b"""
ex foo
""", use_dump=use_dump)
        self.assertTrue(b'Source: Room Zero' in result)
    
    def test_dump(self):
        self._test(use_dump=True)
    
    def test_nodump(self):
        self._test(use_dump=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
