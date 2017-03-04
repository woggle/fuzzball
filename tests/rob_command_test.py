#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

class TestRob(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'penny': 'PENNY',
        'cpenny': 'CPENNY',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def test_unlocked(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@create TestObject
drop TestObject
@succ me=Successfully robbed!
@osucc me={null:{store:true,did_rob}}
@propset me=int:@/value:100
""")
        result = self._do_full_session(b"""
connect TestUser foo
rob TestObject
rob One
score
""")
        self.assertTrue(b'can only rob other players' in result)
        self.assertTrue(b'Successfully robbed!' in result)
        self.assertTrue(b'You stole a PENNY' in result)
        self.assertTrue(b'You have 170 PENNIES' in result)
        result_post = self._do_full_session(CONNECT_GOD +
b"""
ex me=/did_rob
score
""")
        self.assertTrue(b'- str /did_rob:true' in result_post)
        self.assertTrue(b'You have 99 PENNIES' in result_post)

    def test_locked(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@lock me=me
@propset me=int:@/value:100
@fail me=You failed to rob!
@ofail me={null:{store:true,did_fail_rob}}
""")
        result = self._do_full_session(b"""
connect TestUser foo
rob One
score
""")
        self.assertTrue(b'You failed to rob!' in result)
        self.assertTrue(b'You have 169 PENNIES' in result)
        result_post = self._do_full_session(CONNECT_GOD +
b"""
ex me=/did_fail_rob
score
""")
        self.assertTrue(b'- str /did_fail_rob:true' in result_post)
        self.assertTrue(b'You have 100 PENNIES' in result_post)

    def test_nopennies(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@pcreate TestUser=foo
@propset me=int:@/value:0
@succ me=ROBBED-SUCC
@fail me=ROBBED-FAIL
""")
        result = self._do_full_session(b"""
connect TestUser foo
rob One
score
""")
        self.assertTrue(b'ROBBED-SUCC' not in result)
        self.assertTrue(b'ROBBED-FAIL' not in result)
        self.assertTrue(b'One has no PENNIES' in result)

class TestKillRestricted(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'penny': 'PENNY',
        'cpenny': 'CPENNY',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
        'restrict_kill': 'yes'
    }
    def test_me_not_kill_ok(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@set me=!K
kill One
""")
        self.assertTrue(b'You have to be set Kill_OK' in result)

class TestGive(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'penny': 'PENNY',
        'cpenny': 'CPENNY',
        'start_pennies': '169',
    }

    def test_give_wizard_to_player(self):
        result = self._do_full_session(CONNECT_GOD +
b"""
@propset me=int:@/value:100
give me=1000
score
""")
        self.assertTrue(b'You have 1100 PENNIES' in result)
        
    def test_give_notwizard(self):
        result_setup = self._do_full_session(CONNECT_GOD +
b"""
@propset me=int:@/value:100
@pcreate Foo=test
""")
        result = self._do_full_session(
b"""
connect Foo test
give One=15
give One=200
score
""")
        self.assertTrue(b'You give 15 PENNIES to One' in result)
        self.assertTrue(b"You don't have that many PENNIES" in result)
        self.assertTrue(b'You have 154 PENNIES' in result)
        result_post = self._do_full_session(CONNECT_GOD +
b"""
score
""")
        self.assertTrue(b'You have 115 PENNIES' in result_post)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
