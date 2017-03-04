#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestExamineThing(ServerTestBase):
    SETUP_THING = b"""
@create Foo
@chlock Foo=_chlocktest:1
@flock Foo=_flocktest:1
@conlock Foo=_conlocktest:1
@readlock Foo=_readlocktest:1
@linklock Foo=_linklocktest:1
@lock Foo=_locktest:1
@describe Foo={null:description}
@drop Foo=Drop message.
@odrop Foo=Odrop message.
@idesc Foo={null:inside description}
@pecho Foo=Foo pecho>>> 
@oecho Foo=Foo oecho>>> 
@set Foo=_testprop:42
@propset Foo=int:~testint:43
@propset Foo=dbref:@testref:#1
@propset Foo=lock:_testlock:_foo:1
@propset Foo=float:_testfloat:42.0
@set Foo=_testdir:normalvalue
@set Foo=_testdir/innervalue:xyz
@set Foo=_testdir/outervalue:xyz
@set Foo=_blessprop:{null:}
@bless Foo=_blessprop
"""
    def test_examine_props(self):
        result = self._do_full_session(CONNECT_GOD + self.SETUP_THING +
b"""
examine Foo=/
""")
        self.assertTrue(b'- dir /_/' in result)
        self.assertTrue(b'- int /~testint:43' in result)
        self.assertTrue(b'- ref /@testref:One(#1' in result)
        self.assertTrue(b'- lok /_testlock:_foo:1' in result)
        self.assertTrue(b'- flt /_testfloat:42' in result)
        self.assertTrue(b'- str /_testdir/:normalvalue' in result)
        self.assertTrue(b'B str /_blessprop:{null:}' in result)

    def test_examine_propdir(self):
        result = self._do_full_session(CONNECT_GOD + self.SETUP_THING +
b"""
examine Foo=/_testdir/
""")
        self.assertTrue(b'- str /_testdir/innervalue:xyz' in result)
        self.assertTrue(b'- str /_testdir/outervalue:xyz' in result)
        self.assertTrue(b'2 properties listed' in result)

    def test_plain_examine(self):
        result = self._do_full_session(CONNECT_GOD + self.SETUP_THING +
b"""
examine Foo
""")
        self.assertTrue(b'Foo(#2)  Owner: One  Value: 1' in result)
        self.assertTrue(b'Type: THING' in result)
        self.assertTrue(b'\n{null:description}' in result)
        self.assertTrue(b'Idesc: {null:inside description}' in result)
        self.assertTrue(b'Drop: Drop message.' in result)
        self.assertTrue(b'Odrop: Odrop message.' in result)
        self.assertTrue(b'Chown_OK Key: _chlocktest:1' in result)
        self.assertTrue(b'Link_OK Key: _linklocktest:1' in result)
        self.assertTrue(b'Force Key: _flocktest:1' in result)
        self.assertTrue(b'Container Key: _conlocktest:1' in result)
        self.assertTrue(b'Read Key: _readlocktest:1' in result)
        self.assertTrue(b'Pecho: Foo pecho>>>' in result)
        self.assertTrue(b'Oecho: Foo oecho>>>' in result)

    def test_noprivs(self):
        result_setup = self._do_full_session(CONNECT_GOD + self.SETUP_THING +
b"""
@pcreate TestUser=foo
@desc Foo=Test {null:with MPI}description.
drop Foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
ex Foo
l Foo
""")
        self.assertTrue(b'Owner: One' in result)
        self.assertTrue(b'Test description.' in result)


class TestThingContents(ServerTestBase):
    def test_empty_contents(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
@contents Foo
""")
        self.assertTrue(b'0 objects found' in result)

    def test_nonempty_contents(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
@create Bar
@conlock Foo=me|!me
put Bar=Foo
@contents Foo
""")
        self.assertTrue(b'\n1 ' in result)
        self.assertTrue(b'Bar(#3)\r\n***End of List' in result)

class TestExamineAction(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig Alpha
@action foo=me
@link foo=#2
@succ foo={null:success}
@osucc foo={null:osuccess}
@fail foo={null:failure}
@ofail foo={null:ofailure}
foo
foo
examine foo
""")
        self.assertTrue(b'foo(#3E)  Owner: One' in result)
        self.assertTrue(b'Type: EXIT/ACTION' in result)
        self.assertTrue(b'Source: One(#1P' in result)
        self.assertTrue(b'Destination: Alpha(#2R' in result)
        self.assertTrue(b'Success: {null:success}' in result)
        self.assertTrue(b'Osuccess: {null:osuccess}' in result)
        self.assertTrue(b'Fail: {null:failure}' in result)
        self.assertTrue(b'Ofail: {null:ofailure}' in result)
        self.assertTrue(b'Usecount: 2' in result)


class TestExamineRoom(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig Alpha=#0
@dig Beta=#2
@desc #3={null:Test description with MPI.}
@linklock #3=_linklock:1
examine #3
""")
        self.assertTrue(b'Parent: Alpha(#2' in result)
        self.assertTrue(b'\r\n{null:Test description with MPI.}' in result)
        self.assertTrue(b'Owner: One' in result)
        self.assertTrue(b'Type: ROOM' in result)
        self.assertTrue(b'Link_OK Key: _linklock:1' in result)
        self.assertTrue(b'No exits.' in result)

class TestCreateExaminePlayer(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@dig Alpha=#0
@tune player_start=#2
@tune start_pennies
@pcreate TestPlayer=test
@desc *TestPlayer={null:Test description with MPI.}
@create Foo
@tel Foo=*TestPlayer
@dig Beta=#0
@act testAct=#3
@tel *TestPlayer=#5
""",
b"""
examine *TestPlayer
""", use_dump=use_dump)
        self.assertTrue(b'TestPlayer(#3PBH' in result)
        self.assertTrue(b'CPENNIES: 169' in result)
        self.assertTrue(b'\r\n{null:Test description with MPI.}' in result)
        self.assertTrue(b'Type: PLAYER' in result)
        self.assertTrue(b'Home: Alpha(#2R' in result)
        self.assertTrue(b'Location: Beta(#5R' in result)
        self.assertTrue(b'Carrying:\r\nFoo(#4)' in result)
        self.assertTrue(b'Actions/exits:\r\ntestAct(#6E' in result)
    
    def test_nodump(self):
        self._test(use_dump=False)

    def test_dump(self):
        self._test(use_dump=True)

class TestScore(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
    }
    def test_dump(self):
        result = self._do_dump_test(CONNECT_GOD +
b"""
@pcreate TestUser=foo
""", b"""
connect TestUser foo
score
""", prefix=b'')
        self.assertTrue(b'You have 169 PENNIES.' in result)

    def test_nodump(self):
        result_setup = self._do_full_session(CONNECT_GOD + 
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
score
""")
        self.assertTrue(b'You have 169 PENNIES.' in result)

class TestOwned(ServerTestBase):
    def test_simple(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@create TestObject
@chown TestObject=TestUser
""")
        result = self._do_full_session(b"""
connect TestUser foo
@owned
""")
        self.assertTrue(b'TestObject' in result)

class TestFind(ServerTestBase):
    def test_simple_positive(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@dig IdThree
@tel #2=#3
@find IdTw
""")
        self.assertTrue(b'IdTwo(#2)\r\n***End' in result)

class TestInventory(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foobar
inventory
""")
        self.assertTrue(b'You are carrying:\r\nFoobar' in result)

class TestEntrances(ServerTestBase):
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@dig Alpha
@act foo=here
@link foo=#2
@act bar;baz;quux=me
@link bar=#2
@link me=#2
""",
b"""
say Before
@entrances #2
""", use_dump=use_dump)
        result_after = result.split(b'Before')[1]
        self.assertTrue(b'\nfoo(#3E' in result)
        self.assertTrue(b'\nbar;baz;quux(#4E' in result)
        self.assertTrue(b'\nOne(#1P' in result)
        self.assertTrue(b'\n3 objects' in result)

    def test_dump(self):
        self._test(use_dump=True)

    def test_nodump(self):
        self._test(use_dump=False)

class TestSweep(ServerTestBase):
    def test_negative(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@sweep
""")
        self.assertTrue(b'One(#1PWM3) is a player.' in result)

    def test_listener_room_muf(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
: main "x" ;
.
c
q
@propset here=dbref:_listen/testlisten:test.muf
@sweep
""")
        self.assertTrue(b'Room Zero(#0R) is a listening room.' in result)

    def test_listener_thing_muf(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
drop Foo
@program test.muf
i
: main me @ swap notify ;
.
c
q
@set Foo=_listen/test:3
@sweep
""")
        self.assertTrue(b'Foo(#2) is a listener object owned by One(#1PWM3).' in result)

    def test_say_trap_nomuf(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
drop Foo
@act say=Foo
@link say=Foo
@set say=H
@lock say=me&!me
@fail say=triggered
say test
@sweep
""")
        self.assertTrue(b'says are trapped' in result)

    def test_say_trap_muf(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
drop Foo
@act say=Foo
@set say=H
@lock say=me&!me
@program test.muf
.
q
@link say=test.muf
@fail say=triggered
say test
@sweep
""")
        self.assertTrue(b'says are trapped' in result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
