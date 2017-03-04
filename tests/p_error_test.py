#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestSetClearError(MufProgramTestBase):
    def test_set_clear(self):
        result = self._test_program(b"""
: main
    error? if "error initially set" abort then
    "DIV_ZERO" set_error not if "failed set DIV_ZERO" abort then
    error? not if "error? false" abort then
    "IBOUNDS" set_error not if "failed set IBOUNDS" abort then
    "DIV_ZERO" is_set? not if "DIV_ZERO unset" abort then
    "IBOUNDS" is_set? not if "IBOUNDS unset" abort then
    err_divzero? not if "err_divzero? false" abort then
    err_ibounds? not if "err_ibounds? false" abort then
    "IBOUNDS" clear_error
    err_ibounds? if "err_ibounds? true" abort then
    0 clear_error
    err_divzero? if "err_divzero? true" abort then
    error? if "error? true" abort then
    0 error_name "DIV_ZERO" strcmp if "0 error_name not DIV_ZERO" abort then
    0 error_str "division by zero" instring not if "0 error_str does not contain division by zero" abort then
    "DIV_ZERO" error_bit 0 = not if "DIV_ZERO error_bit is not 0" abort then
    "DIV_ZERO" set_error "IBOUNDS" set_error
    clear
    error? if "error? true" abort then
    err_divzero? if "err_divzero? true" abort then
    err_ibounds? if "err_ibounds? true" abort then
    me @ "Test passed." notify
;
""")
    
    def test_error_num(self):
        result = self._test_program(b"""
: main
    error_num 5 = if
        me @ "Test passed." notify
    then
;
""")
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
