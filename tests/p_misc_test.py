#!/usr/bin/env python3.6
import asyncio
import datetime
import logging
import re
import time
import unittest

from fbmuck.server import Server, ServerTestBase, MufProgramTestBase, CONNECT_GOD

class TestQueue(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    "FromQueue" strcmp not if
        trig #-1 =
        loc @ #-1 = and
        if
            me @ "Test passed." notify
        then
        prog "_finished" 1 setprop
    else
        #-1 loc !
        0 prog "FromQueue" queue
        dup 0 = if "no PID" abort then
        begin
            0 sleep
            prog "_finished" getprop 1 = not while
        repeat
    then

;
""")

class TestKill(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    "FromQueue" strcmp not if
        prog "_started" 1 setprop
        me @ "FAILED" notify
        begin 0 sleep repeat
    else
        #-1 loc !
        preempt
        0 prog "FromQueue" queue
        dup kill 1 =
        swap kill 0 =
        and
        foreground
        0 sleep
        prog "_started" getprop 0 =
        and if me @ "Test passed." notify then
    then
;
""")
        self.assertTrue(b'\nFAILED' not in result)

class TestFork(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    var parentpid pid parentpid !
    var childpid
    fork dup 0 = if
        me @ "_child_done" pid setprop
    else
        childpid !
        begin 0 sleep
            me @ "_child_done" getprop
            0 = while
        repeat
        me @ "_child_done" getprop
        childpid @ = if me @ "Test passed." notify then
    then
;
""")

class TestStats(MufProgramTestBase):
    def test_simple_all(self):
        self._test_program(rb"""
: main
    #-1 stats 7 array_make
    { 4 1 1 0 1 1 0 }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

    def test_simple_One(self):
        self._test_program(rb"""
: main
    #1 stats 7 array_make
    { 4 1 1 0 1 1 0 }list array_compare 0 =
    if me @ "Test passed." notify then
;
""")

class TestIsPidP(MufProgramTestBase):
    def test_simple(self):
        self._test_program(rb"""
: main
    "FromQueue" strcmp not if exit then
    1
    pid ispid? and
    -1 ispid? not and
    1000000 ispid? not and
    120 prog "FromQueue" queue dup ispid? over kill pop swap ispid? not and and
    if me @ "Test passed." notify then
;
""")

class TestForce(MufProgramTestBase):
    def test_simple(self):
        result = self._test_program(rb"""
: main
    "Foo" "pass" newplayer
    "say This is a test string." force
;
""", before=b"""
@set test.muf=W
""", pass_check=False)
        self.assertTrue(b'Foo says, "This is a test string."' in result)

    def test_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        "arg" strcmp not
        command @ "testcmd" strcmp not and
        force_level 0 > and
        forcedby prog = and
        if #1 "Test passed." notify then
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd arg" force
    then
;
""", before=b"""
@set test.muf=W
""")

    def test_double_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        dup "first" strcmp not if
            me @ "testcmd second" force
        else
            "second" strcmp not
            command @ "testcmd" strcmp not and
            force_level 1 > and
            forcedby prog = and
            forcedby_array { prog prog }list array_compare 0 = and
            if #1 "Test passed." notify then
        then
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd first" force
    then
;
""", before=b"""
@set test.muf=W
""")

    def test_over_recursive(self):
        result = self._test_program(rb"""
: main
    me @ name "Foo" strcmp not if
        0 try
            me @ "testcmd" force
        catch
            "call loops" instring if #1 "Test passed." notify then
        endcatch
    else
        "Foo" "pass" newplayer
        dup "testcmd" newexit prog setlink
        "testcmd first" force
    then
;
""", before=b"""
@set test.muf=W
""")

class TestSysparm(MufProgramTestBase):
    extra_params = {
        'pennies': 'XXX',
        'cpennies': 'YYY',
    }

    def test_read_param_simple_array_foreach(self):
        self._test_program(rb"""
: main
    "*" sysparm_array foreach swap pop
        dup "name" [] "pennies" strcmp not if
            "value" [] "XXX" strcmp not
            if me @ "Test passed." notify then
        else pop then
    repeat
;
""")

    def test_read_param_simple_array_single(self):
        self._test_program(rb"""
: main
    "pennies" sysparm_array 0 []
        dup "name" [] "pennies" strcmp not if
            "value" [] "XXX" strcmp not
            if me @ "Test passed." notify then
        then
;
""")

    def test_read_param_simple(self):
        self._test_program(rb"""
: main
    "pennies" sysparm "XXX" strcmp not
    if me @ "Test passed." notify then
;
""")

    def test_set_param_simple(self):
        self._test_program(rb"""
: main
    "pennies" "ZZZ" setsysparm
    "pennies" sysparm "ZZZ" strcmp not
    if me @ "Test passed." notify then
;
""", before=rb"""
@set test.muf=W
""")

class TestDateTimeUTC(MufProgramTestBase):
    timezone = 'UTC'
    def test_time_okay(self):
        result =  self._test_program(rb"""
: main
    me @ time "T=%02i:%02i:%02i" fmtstring notify
;
""", pass_check=False)
        m = re.search(rb'\nT=(?P<h>\d+):(?P<m>\d+):(?P<s>\d+)', result)
        self.assertTrue(m)
        values = m.group()
        found_time = datetime.time(
            hour=int(m.group('h')),
            minute=int(m.group('m')),
            second=int(m.group('s')),
        )
        now_datetime = datetime.datetime.utcnow()
        now_date = datetime.date.today()
        found_dt_guess = datetime.datetime.combine(now_date, found_time)
        possible_dts = [
            found_dt_guess,
            found_dt_guess - datetime.timedelta(days=1),
            found_dt_guess + datetime.timedelta(days=1)
        ]
        offsets = list(map(lambda t: abs((t - now_datetime).total_seconds()), possible_dts))
        self.assertTrue(min(offsets) < 10.0)

    def test_date_okay(self):
        result =  self._test_program(rb"""
: main
    me @ date "D=%02i/%02i/%02i" fmtstring notify
;
""", pass_check=False)
        m = re.search(rb'\nD=(?P<y>\d+)/(?P<m>\d+)/(?P<d>\d+)', result)
        self.assertTrue(m)
        values = m.group()
        found_date = datetime.date(
            year=int(m.group('y')),
            month=int(m.group('m')),
            day=int(m.group('d')),
        )
        now_date = datetime.date.today()
        delta = abs(now_date.toordinal() - found_date.toordinal())
        self.assertTrue(delta <= 1)

    def test_gmtoffset(self):
        self._test_program(rb"""
: main
    gmtoffset 0 = if me @ "Test passed." notify then
;
""")

    def test_systime(self):
        result =  self._test_program(rb"""
: main
    me @ systime "T=%02i" fmtstring notify
;
""", pass_check=False)
        m = re.search(rb'\nT=(?P<t>\d+)', result)
        self.assertTrue(m)
        raw_time = int(m.group('t'))
        self.assertTrue( abs(raw_time - time.time()) < 10.0 )

    def test_systime_precise(self):
        result =  self._test_program(rb"""
: main
    me @ systime_precise "T=%.2f" fmtstring notify
;
""", pass_check=False)
        m = re.search(rb'\nT=(?P<t>[\d.]+)', result)
        self.assertTrue(m)
        raw_time = float(m.group('t'))
        self.assertTrue( abs(raw_time - time.time()) < 10.0 )


    def test_timesplit_simple(self):
        result = self._test_program(rb"""
: main
    1
    0 timesplit 8 array_make
    { 0 0 0 1 1 1970 5 1 }list array_compare 0 = and
    2000000000 timesplit 8 array_make
    { 20 33 3 18 5 2033 4 138 }list array_compare 0 = and
    if me @ "Test passed." notify then
;
""")

    def test_timefmt_simple(self):
        result = self._test_program(rb"""
: main
    1
    2000000000
    "%a/%A/%b/%B/%d/%e/%H/%I/%M/%S/%p/%Y/%l/%k" swap timefmt
    "Wed/Wednesday/May/May/18/18/03/03/33/20/AM/2033/ 3/ 3" strcmp not and
    10000000
    "%a/%A/%b/%B/%d/%e/%H/%I/%M/%S/%p/%Y/%l/%k" swap timefmt
    "Sun/Sunday/Apr/April/26/26/17/05/46/40/PM/1970/ 5/17" strcmp not and
    if me @ "Test passed." notify then
;
""")

    def test_create_timestamp(self):
        result = self._test_program(rb"""
: main
    systime var start_time start_time !
    #0 "TestObject" newobject timestamps
    systime var done_time done_time !
    pop (use count)
    pop (last used)
    pop (modified)
    dup start_time @ >= swap done_time @ <= and if
        me @ "Test passed." notify
    then
;
""")

    def test_modify_timestamp(self):
        result = self._test_program(rb"""
: main
    systime var start_time start_time !
    #0 "_testprop" 1 setprop #0 timestamps
    systime var done_time done_time !
    pop (use count)
    pop (last used)
    swap pop (create)
    dup start_time @ >= swap done_time @ <= and if
        me @ "Test passed." notify
    then
;
""")

class TestCanCall(MufProgramTestBase):
    def test_call_self(self):
        result = self._test_program(rb"""
: foo ;
PUBLIC foo
: main
    1
    prog "foo" cancall? and
    prog "bar" cancall? not and
    if me @ "Test passed." notify then
;
""")
    
    def test_call_other_owned_uncompiled(self):
        result = self._test_program(rb"""
: main
    "OtherProgram.muf" match 
    1 
    over "foo" cancall? and
    over "bar" cancall? not and
    if me @ "Test passed." notify then
;
""",
before=rb"""
@program OtherProgram.muf
1 i
: foo ;
PUBLIC foo
: bar ;
: main ;
.
q
""")

    def test_call_other_linkable_uncompiled(self):
        result = self._test_program(rb"""
: main
    "OtherProgram.muf" match 
    1 
    over "foo" cancall? and
    over "bar" cancall? not and
    if me @ "Test passed." notify then
;
""",
before=rb"""
@program OtherProgram.muf
1 i
: foo ;
PUBLIC foo
: bar ;
: main ;
.
q
@pcreate TestUser=foo
@set TestUser=3
@chown OtherProgram.muf=TestUser
@set OtherProgram.muf=L
""")

    def test_call_other_unlinkable_uncompiled(self):
        result = self._test_program(rb"""
: main
    "OtherProgram.muf" match 
    1 
    over "foo" cancall? not and
    over "bar" cancall? not and
    if me @ "Test passed." notify then
;
""",
before=rb"""
@program OtherProgram.muf
1 i
PUBLIC foo
: foo ;
: bar ;
: main ;
.
q
@pcreate TestUser=foo
@set TestUser=3
@chown OtherProgram.muf=TestUser
""")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
