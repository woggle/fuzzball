#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD


class TestBoot(ServerTestBase):
    def test_one_conn(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@set *TestUser=W
""")
        result = self._do_full_session(b"""
connect TestUser foo
@boot TestUser
""", autoquit=False)
        self.assertTrue(b'You have been booted' in result)


class TestToadNoRecycle(ServerTestBase):
    extra_params = { 'toad_recycle': 'no' }

    def test_toad_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@toad TestUser
ex #2
""")
        self.assertTrue(b'toad named TestUser' in result)

    def test_toad_owning(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@pcreate NewUser=bar
@create IdFour
@chown IdFour=TestUser
@tel IdFour=TestUser
@toad TestUser=NewUser
ex #4
""")
        self.assertTrue(b'Owner: NewUser' in result)


class TestForce(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
        'zombies': 'yes'
    }

    def test_as_wizard_force_player(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate Foo=pass
@force Foo=@create Bar
ex #3
""")
        self.assertTrue(b'Owner: Foo' in result)

    def test_as_player_force_zombie(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
@create Foo
@set Foo=z
@flock Foo=me
@set Foo=X
drop Foo
@force Foo=@set me=_test:bar
ex Foo=_test
""")
        self.assertTrue(b'- str /_test:bar' in result)

    def test_as_player_force_zombie_bad_flock(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
@create Foo
@set Foo=z
@flock Foo=me&!me
@set Foo=X
drop Foo
@force Foo=@set me=_test:bar
""")
        self.assertTrue(b'not force-locked' in result)


class TestStats(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@stats
""")
        self.assertTrue(b'1 room' in result)
        self.assertTrue(b'0 exit' in result)
        self.assertTrue(b'1 player' in result)


class TestTeleport(ServerTestBase):
    def test_tohome_player(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@dig Beta
@link TestUser=#3
@tel TestUser=home
ex *TestUser
""")
        self.assertTrue(b'Location: Beta' in result)

    def test_tohome_thing(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create TestThing
@dig Beta
@link TestThing=#3
@tel TestThing=home
ex #2
""")
        self.assertTrue(b'Location: Beta' in result)


    def test_parent_loop_thing(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@create IdThree
@create IdFour
@tel #4=#3
@tel #3=#2
@tel #2=#4
""")
        self.assertTrue(b'contain itself' in result)

    def test_parent_loop_player(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@create IdThree
@set IdThree=V
@create IdFour
@set IdFour=V
@tel IdThree=TestUser
@tel #4=#3
@tel TestUser=#4
""")
        self.assertTrue(b'contain themselves' in result)

    def test_dropto(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@dig IdThree
@dig IdFour
@link #3=#4
@tel IdTwo=#3
ex #2
""")
        self.assertTrue(b'Location: IdFour' in result)

    def test_nomatch(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@tel IdTwo=badname
""")
        self.assertTrue(b'Send it where?' in result)


class TestWall(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@wall Hello world.
""")
        self.assertTrue(b'One shouts, "Hello world."' in result)


class TestUnbless(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Foo
@set Foo=_test:foo
@bless Foo=_test
ex Foo=_test
@unbless Foo=_test
ex foo=_test
""")
        self.assertTrue(b'B str' in result)
        self.assertTrue(b'- str' in result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
