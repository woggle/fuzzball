#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD


class TestMufCompileErrors(ServerTestBase):
    def test_uncompilable_unknown_public(self):
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
PUBLIC foo
.
c
q
""")
        self.assertTrue(rb'Subroutine unknown' in result)
    
    def test_uncompilable_double_public(self):
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
: foo ;
PUBLIC foo
PUBLIC foo
.
c
q
""")
        self.assertTrue(rb'already declared' in result)
    
    def test_uncompilable_variable_limit(self):
        var_list = b"\n".join(map(lambda s: "var x{}".format(s).encode(), range(500)))
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
""" + var_list + rb"""
.
c
q
""")
        self.assertTrue(rb'exceeded' in result)

    def test_uncompilable_lvariable_limit(self):
        var_list = b"\n".join(map(lambda s: "lvar x{}".format(s).encode(), range(500)))
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
""" + var_list + rb"""
.
c
q
""")
        self.assertTrue(rb'exceeded' in result)
    
    def test_uncompilable_svariable_limit(self):
        var_list = b"\n".join(map(lambda s: "var x{}".format(s).encode(), range(500)))
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
: foo
""" + var_list + rb"""
;
.
c
q
""")
        self.assertTrue(rb'exceeded' in result)
    
    def test_uncompilable_svariable_excl_limit(self):
        var_list = b"\n".join(map(lambda s: "var! x{}".format(s).encode(), range(500)))
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
: foo
""" + var_list + rb"""
;
.
c
q
""")
        self.assertTrue(rb'exceeded' in result)

    def test_uncompilable_bad_version(self):
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
$version foobar
.
c
q
""")
        self.assertTrue(rb'number for the version' in result)
    
    def test_uncompilable_bad_lib_version(self):
        result = self._do_full_session(CONNECT_GOD +
rb"""
@program foo.muf
i
$lib-version foobar
.
c
q
""")
        self.assertTrue(rb'number for the version' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
