#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MPITestBase

CONNECT = b"connect One potrzebie\n"

class TestBlankAction(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo;foobar=me
@link foo=me
@lock foo=me&!me
@fail foo=Triggered failure message cmd="{&cmd}" arg="{&arg}"
@succ foo=Triggered success message.
@set foo=H
foo Arguments here
foobar More arguments here
""")
        self.assertTrue(b'Triggered failure message cmd="foo" arg="Arguments here"' in result)
        self.assertTrue(b'Triggered failure message cmd="foobar" arg="More arguments here"' in result)

class TestBlankActionSpecialName(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo;say;pose;delimiter=me
@link foo=me
@lock foo=me&!me
@fail foo=Triggered failure message cmd="{&cmd}" arg="{&arg}"
@succ foo=Triggered success message.
@set foo=H
"As say.
:As pose.
;As delimiter.
@name foo=foo
""")
        self.assertTrue(b'Triggered failure message cmd="say" arg="As say."' in result)
        self.assertTrue(b'Triggered failure message cmd="pose" arg="As pose."' in result)
        self.assertTrue(b'Triggered failure message cmd="delimiter" arg="As delimiter."' in result)

class TestMPIOverflow(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo=me
@link foo=me
@lock foo=me&!me
@fail foo={exec:_/fl}
@set foo=H
foo 
""")
        self.assertTrue(b' Recursion limit exceeded.' in result)

class TestMPIForceOverflow(ServerTestBase):
    def test(self):
        result1 = self._do_full_session(CONNECT +
b"""
@pcreate TestPlayer=test
@action foo=here
@link foo=here
@lock foo=me&!me
@fail foo={force:*TestPlayer,foo}
@bless foo=_/fl
@set foo=H
""")
        result2 = self._do_full_session(
b"""connect TestPlayer test
foo 
""")
        self.assertTrue(b"You can't force recursively" in result2)

class TestMPILockOverflow(ServerTestBase):
    def test(self):
        result1 = self._do_full_session(CONNECT +
b"""
@action foo=here
@link foo=here
@lock foo=_fooprop:42
@set foo=_fooprop:{if:{locked:me,#2},42,0}
@succ foo=Foo success.
@fail foo=Foo failure.
foo
""")
        logging.error("result1 = %s", result1);
        self.assertTrue(b'Foo failure.' in result1)


class TestMPIFunc(MPITestBase):
    def test_threearg(self):
        self._test_mpi(rb"{func:foo,va,vb,vc,func({&va}:{&vb}:{&vc})}"
                      +rb"{if:{eq:{foo:x,y,z},func(x:y:z)},Test passed.}")

class TestMPIProp(MPITestBase):
    def test_direct(self):
        self._test_mpi(rb"{if:{eq:{prop:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:testvalue
""")
    
    def test_direct_exact(self):
        self._test_mpi(rb"{if:{eq:{prop!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:testvalue
""")

    def test_env(self):
        self._test_mpi(rb"{if:{eq:{prop:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:testvalue
""")

    def test_noenv(self):
        self._test_mpi(rb"{if:{ne:{prop!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:testvalue
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
