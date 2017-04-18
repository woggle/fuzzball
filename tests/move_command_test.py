#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD


class TestHome(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@dig IdTwo
@link me=#2
home
ex me
""")
        self.assertTrue(b'Location: IdTwo(' in result)


class TestVehicleTelLeave(ServerTestBase):
    extra_params = {'vehicles': 'yes'}
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@set IdTwo=V
drop IdTwo
@idesc IdTwo=TestInsideDesc
@tel me=#2
ex me
leave
ex me
""")
        self.assertTrue(b'You exit the' in result)
        self.assertTrue(b'TestInsideDesc' in result)
        self.assertTrue(b'Location: IdTwo' in result)
        self.assertTrue(b'Location: Room Zero' in result)


class TestDropGet(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
drop IdTwo
ex IdTwo
get IdTwo
ex IdTwo
""")
        self.assertTrue(b'Location: Room Zero' in result)
        self.assertTrue(b'Location: One' in result)

class TestGetZombie(ServerTestBase):
    extra_params = {'allow_zombies': 'yes'}
    def test_get_zombie_thief(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@pcreate OtherPlayer=test
@create Zombie
@set Zombie=Z
@create OtherThing
@chown OtherThing=OtherPlayer
@force Zombie=get OtherThing
ex OtherThing
"""
)
        self.assertTrue(b'''Zombie> Zombies aren't allowed to be thieves!''' in result)
        self.assertTrue(b'Location: One' in result)

    # regression for a crash
    def test_get_room_zero(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create Zombie
@set Zombie=Z
drop Zombie
@force Zombie=get #0
""")

class TestRecycle(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@create IdTwo
@recycle IdTwo
ex #2
""")
        self.assertTrue(b'is garbage.' in result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
