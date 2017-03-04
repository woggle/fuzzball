#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase

class TestConstants(MufProgramTestBase):
    def test_inf(self):
        result = self._test_program(b"""
: main
    inf 1.0 0.0 / = if
        me @ "Test passed." notify
    then
;
""")

    def test_pi(self):  
        result = self._test_program(b"""
: main
    pi 3.141 > pi 3.142 < and if
        me @ "Test passed." notify
    then
;
""")

    def test_epsilon(self):  
        result = self._test_program(b"""
: main
    1.0 epsilon + 1.0 > if
        me @ "Test passed." notify
    then
;
""")

class TestCeil(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    1.2 ceil 2.0 = -1.2 ceil -1.0 = and 1.7 ceil 2.0 = and error? not and if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf ceil inf = error? and err_fbounds? and if
        me @ "Test passed." notify
    then
;
""")


class TestFloor(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    1.2 floor 1.0 = -1.2 floor -2.0 = and 1.7 floor 1.0 = and error? not and if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf floor inf = error? and err_fbounds? and if
        me @ "Test passed." notify
    then
;
""")

class TestRound(MufProgramTestBase):
    def test_zero_normal(self):
        result = self._test_program(b"""
: main
    1.2 0 round 1.0 = -1.2 0 round -1.0 = and 1.7 0 round 2.0 = and error? not and if
        me @ "Test passed." notify
    then
;
""")
    
    def test_one_normal(self):
        result = self._test_program(b"""
: main
    1.52 1 round 1.5 = -1.52 1 round -1.5 = and 1.47 1 round 1.5 = and error? not and if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf 0 round pop error? err_fbounds? and if
        me @ "Test passed." notify
    then
;
""")

class TestSqrt(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    4.0 sqrt 2.0 = 0.0 sqrt 0.0 = and error? not and if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf sqrt inf = error? and err_fbounds? and if
        me @ "Test passed." notify
    then
;
""")

    def test_error_imaginary(self):
        result = self._test_program(b"""
: main
    -1.0 sqrt pop error? err_imaginary? and if
        me @ "Test passed." notify
    then
;
""")


class TestSin(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 sin 0.0 = 
    pi 2.0 / sin 1.0 - fabs 0.001 < and
    pi 6.0 / sin 0.5 - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf sin pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestCos(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 cos 1.0 = 
    pi 2.0 / cos 0.0 - fabs 0.001 < and
    pi 3.0 / cos 0.5 - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf cos pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestTan(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 tan 0.0 = 
    pi 4.0 / tan 1.0 - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf tan pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_nan(self):
        result = self._test_program(b"""
: main
    pi 2.0 / tan pop error? err_nan? and
    if
        me @ "Test passed." notify
    then
;
""")

class TestAsin(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 asin 0.0 = 
    1.0 asin pi 2.0 /  - fabs 0.001 < and
    -0.5 asin pi -6.0 /  - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf asin pop error? err_nan? and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_bounds(self):
        result = self._test_program(b"""
: main
    3.0 asin pop error? err_nan? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestAcos(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 acos pi 2.0 / - fabs 0.001 <
    1.0 acos 0.0 = and
    -0.5 acos pi 3.0 / 2.0 * - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf acos pop error? err_nan? and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_bounds(self):
        result = self._test_program(b"""
: main
    3.0 acos pop error? err_nan? and
    if
        me @ "Test passed." notify
    then
;
""")

class TestAtan(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 atan 0.0 =
    1.0 atan pi 4.0 / - fabs 0.001 < and
    -1.0 atan pi -4.0 / - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_inf(self):
        result = self._test_program(b"""
: main
    inf atan pi 2.0 / - fabs 0.001 <
    if
        me @ "Test passed." notify
    then
;
""")

class TestAtan2(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 0.0 atan2 0.0 =
    1.0 1.0 atan2 pi 4.0 / - fabs 0.001 < and
    -1.0 -1.0 atan2 pi -3.0 * 4.0 / - fabs 0.001 < and
    0.0 1.0 atan2 0.0 - fabs 0.001 < and
    0.0 -1.0 atan2 pi - fabs 0.001 < and
    1.0 0.0 atan2 pi 2.0 / - fabs 0.001 < and
    -1.0 0.0 atan2 pi -2.0 /  - fabs 0.001 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")


class TestDist3D(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    2.0 3.0 4.0 dist3d 5.385 - fabs 0.01 < 
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")


class TestDiff3(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    2.0 3.0 4.0 -1.0 3.0 5.0 diff3
    1.0 = swap 0.0 = and swap -3.0 = and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_wrong_arg(self):
        result = self._test_program(b"""
: main
    "bad type" 3.0 4.0 -1.0 3.0 5.0 6 try diff3 catch
        me @ "Test passed." notify
    endcatch
;
""")


class TestXyzToPolar(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 0.0 0.0 xyz_to_polar 0.0 = swap 0.0 = and swap 0.0 = and
    3.0 -4.0 5.0 xyz_to_polar
        1
        swap pi 4.0 / - fabs 0.001 < and
        swap -4.0 3.0 atan2 - fabs 0.001 < and
        swap 7.071 - fabs 0.01 <  and
    and
    if
        me @ "Test passed." notify
    then
;
""")


class TestPolarToXyz(MufProgramTestBase):
    def test_normal(self):
        result = self._test_program(b"""
: main
    0.0 0.0 0.0 polar_to_xyz 0.0 = swap 0.0 = and swap 0.0 = and
    7.071   -4.0 3.0 atan2  pi 4.0 /   polar_to_xyz
        1
        swap 5.0 - fabs 0.01 < and
        swap -4.0 - fabs 0.01 < and
        swap 3.0 - fabs 0.01 < and
    and
    if
        me @ "Test passed." notify
    then
;
""")


class TestExp(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    0.0 exp 1.0 =  1.0 exp 2.718 - fabs 0.001 < and  error? not and
    if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf exp pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestLog(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    1.0 log 0.0 =  2.718 log 1.0 - fabs 0.01 < and  error? not and
    if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf log inf =  error? err_fbounds? and and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_imaginary(self):
        result = self._test_program(b"""
: main
    -1.0 log pop  error? err_imaginary? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestLog10(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    1.0 log10 0.0 =  10.0 log10 1.0 - fabs 0.01 < and  error? not and
    if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf log10 inf =  error? err_fbounds? and and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_error_imaginary(self):
        result = self._test_program(b"""
: main
    -1.0 log10 pop  error? err_imaginary? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestFAbs(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    1.0 fabs 1.0 =  -1.0 fabs 1.0 = and error? not and
    if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf fabs pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestPow(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    2.0 4.0 pow 16.0 =  2.0 0.0 pow 1.0 =  0.0 0.0 pow 0.0 =  and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_neg_pow(self):
        result = self._test_program(b"""
: main
    -2.0 4.0 pow 16.0 =  error? not and
    if
        me @ "Test passed." notify
    then
;
""")
  
    def test_imaginary(self):
        result = self._test_program(b"""
: main
    -2.0 3.5 pow pop error? err_imaginary? and
    if
        me @ "Test passed." notify
    then
;
""")
    
    def test_error_inf(self):
        result = self._test_program(b"""
: main
    inf inf pow pop error? err_fbounds? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestFMod(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    3.0 0.5 fmod 0.0 - fabs 0.01 < 
    3.0 2.0 fmod 1.0 - fabs 0.01 < and
    1.2 1.1 fmod 0.1 - fabs 0.01 < and
    error? not and
    if
        me @ "Test passed." notify
    then
;
""")

    def test_zero(self):
        result = self._test_program(b"""
: main
    3.0 0.0 fmod pop error? err_divzero? and
    if
        me @ "Test passed." notify
    then
;
""")


class TestStrToF(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    "0.00000" strtof 0.0 - fabs 0.01 < 
    "1.0e0" strtof  1.0 - fabs 0.01 < and
    "0.10000000000" strtof 0.1 - fabs 0.01 < and
    if
        me @ "Test passed." notify
    then
;
""")

class TestFToStr(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(b"""
: main
    0.0 ftostr strtof 0.0 = 
    0.0 ftostrc strtof 0.0 = 
    1.0 4096.0 / ftostr strtof 1.0 4096.0 / = 
    1.0 4096.0 / ftostrc strtof 1.0 4096.0 / = 
    and and and
    if
        me @ "Test passed." notify
    then
;
""")
 
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
