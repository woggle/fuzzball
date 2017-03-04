#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestNameThing(ServerTestBase):
    def test_simplerename(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
@name Foo=Bar
ex Bar
""")
        self.assertTrue(b'Type: THING' in result)

    def test_prohibitedname(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
@name Foo=me
""")
        self.assertTrue(b'That is not a reasonable name' in result)

class TestUnlink(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@dig IdThree
@open foo=#2
@unlink foo
ex foo
""")
        self.assertTrue(b'Destination: ' not in result)

class TestRelink(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@dig IdThree
@open foo=#2
@relink foo=#3
ex foo
""")
        self.assertTrue(b'Destination: IdThree' in result)

    def test_multilink(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@dig IdThree
@create IdFour
@open foo=#2
@relink foo=#3;#4
ex foo
""")
        self.assertTrue(b'Destination: IdThree' in result)
        self.assertTrue(b'Destination: IdFour' in result)

    def test_multilink_no(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@dig IdThree
@program IdFour.muf
q
@open foo=#2
@relink foo=#3;#4
ex foo
""")
        self.assertTrue(b'Only one' in result)
        self.assertTrue(b'Destination IdFour.muf(#4FM3) ignored' in result)
        self.assertTrue(b'Destination: IdTwo' in result)

    def test_loop(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@dig IdThree
@open IdFour=IdTwo
@open IdFive=IdFour
@open IdSix=IdFive
@relink IdFour=IdSix
ex IdFour
""")
        self.assertTrue(b'would create a loop' in result)
        self.assertTrue(b'Destination: IdTwo' in result)


class TestSet(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def _test_clear(self, use_dump):
        result = self._do_dump_test(CONNECT_GOD +
b"""
@create Foo
@set Foo=_/foo/bar/baz:test
@set Foo=:clear
""",b"""
ex Foo=/
""", use_dump=use_dump)
        self.assertTrue(b'0 propert' in result)

    def test_clear_nodump(self):
        self._test_clear(use_dump=False)

    def test_clear_dump(self):
        self._test_clear(use_dump=True)

    def test_clear_priv(self):
        result_setup= self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@create Foo
@set Foo=~specialprop:foobar
@set Foo=_not/~special:bazquux
@chown Foo=TestUser
drop Foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
@set Foo=:clear
ex Foo=/
""")
        self.assertTrue(b'1 propert' in result)
        self.assertTrue(b'~specialprop' in result)


class TestPropset(ServerTestBase):
    def test_erase(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@set me=_test:foo
@propset me=erase:_test
ex me=_test
""")
        self.assertTrue(b'0 properties' in result)

    def test_erase_propdir(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@set me=_test:foo
@set me=_test/bar:baz
@propset me=erase:_test
ex me=_test
""")
        self.assertTrue(b'0 properties' in result)

    def test_erase_prophead(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@set me=_test:foo
@set me=_test/bar:baz
@propset me=int:_test:0
ex me=_test/
ex me=_test
""")
        self.assertTrue(b'- str /_test/bar:baz' in result)
        self.assertTrue(b'1 property' in result)
        self.assertTrue(b'- dir /_test/:(no value)' in result)


class TestGenderProp(ServerTestBase):
    extra_params = {'gender_prop': '_funnygender'}

    def _test_set(self, use_dump):
        result = self._do_dump_test(
b"""
@propset me=str:sex:test
""", b"""
ex me=/
""", use_dump=use_dump
)
        self.assertTrue(b'- str /_funnygender:test' in result)

    def test_set_nodump(self):
        self._test_set(use_dump=False)
    
    def test_set_dump(self):
        self._test_set(use_dump=True)
    
    def test_clear(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@propset me=str:_funnygender:test
@propset me=erase:sex
ex me=/
""")
        self.assertTrue(b'- dir /_/:' in result)
        self.assertTrue(b'1 propert' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
