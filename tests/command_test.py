#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class TestWHOOnePlayer(ServerTestBase):
    extra_params = {
        'who_doing': 'yes',
    }
    def test(self):
        result = self._do_full_session(CONNECT + 
b"""@set me=_/do:Doing message.
!WHO
QUIT
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            b'Player Name' in result
        )
        self.assertTrue(
            re.search(rb'\nOne.*0s\s*.*Doing message.', result)
        )
        self.assertTrue(
            b'Come back later!' in result
        )

class TestWHOOnePlayerNoDoing(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result = self._do_full_session(CONNECT + 
b"""!WHO
QUIT
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            re.search(rb'Player Name\s*Location\s*On For', result)
        )
        self.assertTrue(
            re.search(rb'\nOne.*\s*\[\s*0\s*\]\s*.*\s*(?:127\.|local|::1|0000:)', result)
        )
        self.assertTrue(
            b'Come back later!' in result
        )

class TestWHOOnePlayerNoDoingNoWiz(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result_setup = self._do_full_session(CONNECT + 
b"""
@pcreate TestUser=foo
QUIT
""")
        result = self._do_full_session( 
b"""
connect TestUser foo
@set me=_/do:This should not show.
WHO
QUIT
""")
        result = result.replace(b"\r\n", b"\n")
        logging.debug('output from server is %s (use_ipv6=%s; use_ssl=%s)', result, self.use_ipv6, self.use_ssl)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        self.assertTrue(
            b"### EMPTY MOTD FILE ###" in result
        )
        self.assertTrue(
            b"\nRoom Zero" in result
        )
        self.assertTrue(
            b"\nYou are in Room Zero.  It's very dark here." in result
        )
        self.assertTrue(
            b'Player Name' in result
        )
        # look for start of IPv4 or IPv6 localhost
        self.assertTrue(
            re.search(rb'\nTestUser.*0s', result)
        )
        self.assertFalse(
            re.search(rb'\nTestUser.*This should not', result)
        )
        self.assertTrue(
            b'Come back later!' in result
        )

class TestSayPose(ServerTestBase):
    extra_params = {'huh_mesg': '### HUH ###'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
 asdfasdfasdf
QUIT
""")
        self.assertTrue(b'### HUH ###' in result)


class TestSayPose(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
say Hello 1.
"Hello 2.
pose Hello 3.
:Hello 4.
  say Hello 5.
  "Hello 6.
    pose Hello 7.
    :Hello 8.
QUIT
""")
        self.assertTrue(b'You say, "Hello 1."' in result)
        self.assertTrue(b'You say, "Hello 2."' in result)
        self.assertTrue(b'One Hello 3.' in result)
        self.assertTrue(b'One Hello 4.' in result)
        self.assertTrue(b'You say, "Hello 5."' in result)
        self.assertTrue(b'You say, "Hello 6."' in result)
        self.assertTrue(b'One Hello 7.' in result)
        self.assertTrue(b'One Hello 8.' in result)

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
        result = self._do_full_session(CONNECT + self.SETUP_THING +
b"""
examine Foo=/
QUIT
""")
        self.assertTrue(b'- dir /_/' in result)
        self.assertTrue(b'- int /~testint:43' in result)
        self.assertTrue(b'- ref /@testref:One(#1' in result)
        self.assertTrue(b'- lok /_testlock:_foo:1' in result)
        self.assertTrue(b'- flt /_testfloat:42' in result)
        self.assertTrue(b'- str /_testdir/:normalvalue' in result)
        self.assertTrue(b'B str /_blessprop:{null:}' in result)
    
    def test_examine_propdir(self):
        result = self._do_full_session(CONNECT + self.SETUP_THING +
b"""
examine Foo=/_testdir/
QUIT
""")
        self.assertTrue(b'- str /_testdir/innervalue:xyz' in result)
        self.assertTrue(b'- str /_testdir/outervalue:xyz' in result)
        self.assertTrue(b'2 properties listed' in result)

    def test_plain_examine(self):
        result = self._do_full_session(CONNECT + self.SETUP_THING +
b"""
examine Foo
QUIT
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

class TestThingContents(ServerTestBase):
    def test_empty_contents(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@contents Foo
QUIT
""")
        self.assertTrue(b'0 objects found' in result)

    def test_nonempty_contents(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@create Bar
@conlock Foo=me|!me
put Bar=Foo
@contents Foo
QUIT
""")
        self.assertTrue(b'\n1 ' in result)
        self.assertTrue(b'Bar(#3)\r\n***End of List' in result)

class TestExamineAction(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
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
QUIT
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
        result = self._do_full_session(CONNECT +
b"""
@dig Alpha=#0
@dig Beta=#2
@desc #3={null:Test description with MPI.}
@linklock #3=_linklock:1
examine #3
QUIT
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
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def test(self):
        result = self._do_full_session(CONNECT +
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
examine *TestPlayer
QUIT
""")
        self.assertTrue(b'TestPlayer(#3PBH' in result)
        self.assertTrue(b'CPENNIES: 169' in result)
        self.assertTrue(b'\r\n{null:Test description with MPI.}' in result)
        self.assertTrue(b'Type: PLAYER' in result)
        self.assertTrue(b'Home: Alpha(#2R' in result)
        self.assertTrue(b'Location: Beta(#5R' in result)
        self.assertTrue(b'Carrying:\r\nFoo(#4)' in result)
        self.assertTrue(b'Actions/exits:\r\ntestAct(#6E' in result)

class TestSinglePlayerWhisper(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
whisper One=This is a test.
QUIT
""")
        self.assertTrue(b'You whisper, "This is a test." to One' in result)
        self.assertTrue(b'One whispers, "This is a test."' in result)

class TestSinglePlayerPage(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
page One=This is a test.
QUIT
""")
        self.assertTrue(b'One pages from Room Zero: "This is a test."' in result)

class TestSinglePlayerPageHaven(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@set me=H
page One=This is a test.
QUIT
""")
        self.assertTrue(b'does not wish to be')

class TestHashes(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@hashes all
QUIT
""")
        self.assertTrue(
            re.search(rb'File\s+Hash', result)
        )
        self.assertTrue(
            re.search(rb'interface.c\s+[a-fA-F0-9]+', result)
        )

class TestClone(ServerTestBase):
    extra_params = {'verbose_clone': 0}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@desc Foo={null:to preserve}
@set Foo=@secretprop:42
@propset Foo=dbref:~protectedprop:#0
@propset Foo=lock:_lockprop:me
@clone Foo
ex #3
ex #3=/
QUIT
""")
        self.assertTrue(b'Type: THING' in result)
        self.assertTrue(b'Foo(#3' in result)
        self.assertTrue(b'{null:to preserve}' in result)
        self.assertTrue(b'str /@secretprop:42' in result)
        self.assertTrue(b'ref /~protectedprop:Room Zero' in result)
        self.assertTrue(b'lok /_lockprop:One' in result)


class TestEntrances(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@dig Alpha
@act foo=here
@link foo=#2
@act bar;baz;quux=me
@link bar=#2
@link me=#2
say Before
@entrances #2
QUIT
""")
        result_after = result.split(b'Before')[1]
        self.assertTrue(b'\nfoo(#3E' in result)
        self.assertTrue(b'\nbar;baz;quux(#4E' in result)
        self.assertTrue(b'\nOne(#1P' in result)
        self.assertTrue(b'\n3 objects' in result)

class TestNameThing(ServerTestBase):
    def test_simplerename(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@name Foo=Bar
ex Bar
QUIT
""")
        self.assertTrue(b'Type: THING' in result)

    def test_prohibitedname(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@name Foo=me
QUIT
""")
        self.assertTrue(b'That is not a reasonable name' in result)


 
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
