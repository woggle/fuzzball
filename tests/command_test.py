#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, CONNECT_GOD

CONNECT = CONNECT_GOD

class TestWHOOnePlayer(ServerTestBase):
    extra_params = {
        'who_doing': 'yes',
    }
    def test(self):
        result = self._do_full_session(CONNECT +
b"""@set me=_/do:Doing message.
!WHO
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

class TestWHOOnePlayerNoDoing(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!WHO
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

class TestWHOOnePlayerNoDoingNoWiz(ServerTestBase):
    extra_params = {
        'who_doing': 'no',
    }
    def test(self):
        result_setup = self._do_full_session(CONNECT +
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(
b"""
connect TestUser foo
@set me=_/do:This should not show.
WHO
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

class TestSayPose(ServerTestBase):
    extra_params = {'huh_mesg': '### HUH ###'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
 asdfasdfasdf
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
""")
        self.assertTrue(b'- str /_testdir/innervalue:xyz' in result)
        self.assertTrue(b'- str /_testdir/outervalue:xyz' in result)
        self.assertTrue(b'2 properties listed' in result)

    def test_plain_examine(self):
        result = self._do_full_session(CONNECT + self.SETUP_THING +
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
        result_setup = self._do_full_session(CONNECT + self.SETUP_THING +
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
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@contents Foo
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

class TestSinglePlayerWhisper(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
whisper One=This is a test.
""")
        self.assertTrue(b'You whisper, "This is a test." to One' in result)
        self.assertTrue(b'One whispers, "This is a test."' in result)

class TestSinglePlayerPage(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
page One=This is a test.
""")
        self.assertTrue(b'One pages from Room Zero: "This is a test."' in result)

class TestSinglePlayerPageHaven(ServerTestBase):
    extra_params = {'lookup_cost': '0'}
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@set me=H
page One=This is a test.
""")
        self.assertTrue(b'does not wish to be')

class TestHashes(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@hashes all
""")
        self.assertTrue(
            re.search(rb'File\s+Hash', result)
        )
        self.assertTrue(
            re.search(rb'interface.c\s+[a-fA-F0-9]+', result)
        )

class TestClone(ServerTestBase):
    extra_params = {'verbose_clone': 0}
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@create Foo
@desc Foo={null:to preserve}
@set Foo=@secretprop:42
@propset Foo=dbref:~protectedprop:#0
@propset Foo=lock:_lockprop:me
@set Foo=_proplist/a:foo
@set Foo=_proplist/b:bar
@clone Foo
""",
b"""
ex #3
ex #3=/
ex #3=_proplist/
""", use_dump=use_dump)
        self.assertTrue(b'Type: THING' in result)
        self.assertTrue(b'Foo(#3' in result)
        self.assertTrue(b'{null:to preserve}' in result)
        self.assertTrue(b'str /@secretprop:42' in result)
        self.assertTrue(b'ref /~protectedprop:Room Zero' in result)
        self.assertTrue(b'lok /_lockprop:One' in result)
        self.assertTrue(b'str /_proplist/a:foo' in result)
        self.assertTrue(b'str /_proplist/b:bar' in result)

    def test_dump(self):
        self._test(use_dump=True)
    
    def test_nodump(self):
        self._test(use_dump=False)


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

class TestNameThing(ServerTestBase):
    def test_simplerename(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@name Foo=Bar
ex Bar
""")
        self.assertTrue(b'Type: THING' in result)

    def test_prohibitedname(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foo
@name Foo=me
""")
        self.assertTrue(b'That is not a reasonable name' in result)

class TestTeleport(ServerTestBase):
    def test_tohome_player(self):
        result = self._do_full_session(CONNECT +
b"""
@pcreate TestUser=foo
@dig Beta
@link TestUser=#3
@tel TestUser=home
ex *TestUser
""")
        self.assertTrue(b'Location: Beta' in result)

    def test_tohome_thing(self):
        result = self._do_full_session(CONNECT +
b"""
@create TestThing
@dig Beta
@link TestThing=#3
@tel TestThing=home
ex #2
""")
        self.assertTrue(b'Location: Beta' in result)


    def test_parent_loop_thing(self):
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
b"""
@create IdTwo
@tel IdTwo=badname
""")
        self.assertTrue(b'Send it where?' in result)


class TestStats(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@stats
""")
        self.assertTrue(b'1 room' in result)
        self.assertTrue(b'0 exit' in result)
        self.assertTrue(b'1 player' in result)

class TestVersion(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@version
""")
        self.assertTrue(b'Version: ' in result)

class TestInventory(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@create Foobar
inventory
""")
        self.assertTrue(b'You are carrying:\r\nFoobar' in result)

class TestFind(ServerTestBase):
    def test_simple_positive(self):
        result = self._do_full_session(CONNECT +
b"""
@create IdTwo
@dig IdThree
@tel #2=#3
@find IdTw
""")
        self.assertTrue(b'IdTwo(#2)\r\n***End' in result)

class TestOwned(ServerTestBase):
    def test_simple(self):
        result_setup = self._do_full_session(CONNECT +
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

class TestScore(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
    }
    def test_dump(self):
        result = self._do_dump_test(CONNECT +
b"""
@pcreate TestUser=foo
""", b"""
connect TestUser foo
score
""", prefix=b'')
        self.assertTrue(b'You have 169 PENNIES.' in result)

    def test_nodump(self):
        result_setup = self._do_full_session(CONNECT + 
b"""
@pcreate TestUser=foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
score
""")
        self.assertTrue(b'You have 169 PENNIES.' in result)


class TestBoot(ServerTestBase):
    def test_one_conn(self):
        result_setup = self._do_full_session(CONNECT +
b"""
@pcreate TestUser=foo
@set *TestUser=W
""")
        result = self._do_full_session(b"""
connect TestUser foo
@boot TestUser
""")
        self.assertTrue(b'You have been booted' in result)

class TestToadNoRecycle(ServerTestBase):
    extra_params = { 'toad_recycle': 'no' }
    def test_toad_simple(self):
        result = self._do_full_session(CONNECT +
b"""
@pcreate TestUser=foo
@toad TestUser
ex #2
""")
        self.assertTrue(b'toad named TestUser' in result)

    def test_toad_owning(self):
        result = self._do_full_session(CONNECT +
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

class TestOpen(ServerTestBase):
    def test_one_link(self):
        result = self._do_full_session(CONNECT +
b"""
@dig Beta
@open foo;bar=#2=property
ex me=_reg/property
ex bar
""")
        self.assertTrue(b'Destination: Beta' in result)
        self.assertTrue(b'- ref /_reg/property:foo;bar(#3E' in result)

    def test_two(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@create IdThree
@open foo;bar=#2;#3=property
ex bar
""")
        self.assertTrue(b'Destination: IdTwo' in result)
        self.assertTrue(b'Destination: IdThree' in result)


class TestEdit(ServerTestBase):
    def _test(self, use_dump):
        result = self._do_dump_test(
b"""
@program foo.muf
i
this was the first line
this was the second line
this was the third line
this was the fourth line
.
2 3 d
2 i
this was inserted before the second line
.
q
""",
b"""
@edit foo.muf
n
1 10 l
q
""", use_dump=use_dump)
        self.assertTrue(b'1: this was the first line' in result)
        self.assertTrue(b'2: this was inserted before the second line' in result)
        self.assertTrue(b'3: this was the fourth line' in result)
        self.assertTrue(b'3 lines displayed' in result)

    def test_dump(self):
        self._test(use_dump=True)
    
    def test_nodump(self):
        self._test(use_dump=False)

class TestAttach(ServerTestBase):
    def _test(self, use_dump=False):
        result = self._do_dump_test(
b"""
@act foo=me
@attach foo=#0
""",
b"""
ex foo
""", use_dump=use_dump)
        self.assertTrue(b'Source: Room Zero' in result)
    
    def test_dump(self):
        self._test(use_dump=True)
    
    def test_nodump(self):
        self._test(use_dump=False)

class TestWall(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""
@wall Hello world.
""")
        self.assertTrue(b'One shouts, "Hello world."' in result)

class TestGripe(ServerTestBase):
    extra_params = {'file_log_gripes': 'logs/gripes'}
    def test(self):
        import os.path
        result = self._do_full_session(CONNECT +
b"""
gripe this is a gripe.
""")
        self.assertTrue(b'Your complaint has been' in result)
        with open(os.path.join(self.server.game_dir, 'logs', 'gripes'), 'r') as fh:
            log_text= fh.read()
        self.assertTrue('this is a gripe' in log_text)

class TestRelink(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@dig IdThree
@open foo=#2
@relink foo=#3
ex foo
""")
        self.assertTrue(b'Destination: IdThree' in result)

    def test_multilink(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@dig IdThree
@create IdFour
@open foo=#2
@relink foo=#3;#4
ex foo
""")
        self.assertTrue(b'Destination: IdThree' in result)
        self.assertTrue(b'Destination: IdFour' in result)

    def test_multilink_no(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@dig IdThree
@program IdFour.muf
q
@open foo=#2
@relink foo=#3;#4
ex foo
""")
        self.assertTrue(b'Only one' in result)
        self.assertTrue(b'Destination IdFour.muf(#4FM3) ignored' in result)
        self.assertTrue(b'Destination: IdTwo' in result)

    def test_loop(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@dig IdThree
@open IdFour=IdTwo
@open IdFive=IdFour
@open IdSix=IdFive
@relink IdFour=IdSix
ex IdFour
""")
        self.assertTrue(b'would create a loop' in result)
        self.assertTrue(b'Destination: IdTwo' in result)

class TestUnlink(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT +
b"""
@dig IdTwo
@dig IdThree
@open foo=#2
@unlink foo
ex foo
""")
        self.assertTrue(b'Destination: ' not in result)

class TestGenderProp(ServerTestBase):
    extra_params = {'gender_prop': '_funnygender'}

    def _test_set(self, use_dump):
        result = self._do_dump_test(
b"""
@propset me=str:sex:test
""", b"""
ex me=/
""", use_dump=use_dump
)
        self.assertTrue(b'- str /_funnygender:test' in result)

    def test_set_nodump(self):
        self._test_set(use_dump=False)
    
    def test_set_dump(self):
        self._test_set(use_dump=True)
    
    def test_clear(self):
        result = self._do_full_session(CONNECT +
b"""
@propset me=str:_funnygender:test
@propset me=erase:sex
ex me=/
""")
        self.assertTrue(b'- dir /_/:' in result)
        self.assertTrue(b'1 propert' in result)

class TestPropset(ServerTestBase):
    def test_erase(self):
        result = self._do_full_session(CONNECT +
b"""
@set me=_test:foo
@propset me=erase:_test
ex me=_test
""")
        self.assertTrue(b'0 properties' in result)

    def test_erase_propdir(self):
        result = self._do_full_session(CONNECT +
b"""
@set me=_test:foo
@set me=_test/bar:baz
@propset me=erase:_test
ex me=_test
""")
        self.assertTrue(b'0 properties' in result)

    def test_erase_prophead(self):
        result = self._do_full_session(CONNECT +
b"""
@set me=_test:foo
@set me=_test/bar:baz
@propset me=int:_test:0
ex me=_test/
ex me=_test
""")
        self.assertTrue(b'- str /_test/bar:baz' in result)
        self.assertTrue(b'1 property' in result)
        self.assertTrue(b'- dir /_test/:(no value)' in result)


class TestSweep(ServerTestBase):
    def test_negative(self):
        result = self._do_full_session(CONNECT +
b"""
@sweep
""")
        self.assertTrue(b'One(#1PWM3) is a player.' in result)

    def test_listener_room_muf(self):
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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

class TestHome(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
b"""
@create IdTwo
drop IdTwo
ex IdTwo
get IdTwo
ex IdTwo
""")
        self.assertTrue(b'Location: Room Zero' in result)
        self.assertTrue(b'Location: One' in result)

class TestRecycle(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT +
b"""
@create IdTwo
@recycle IdTwo
ex #2
""")
        self.assertTrue(b'is garbage.' in result)

class TestSet(ServerTestBase):
    extra_params = {
        'cpennies': 'CPENNIES',
        'pennies': 'PENNIES',
        'start_pennies': '169',
        'penny_rate': '0',
        'pcreate_flags': 'BH',
    }
    def _test_clear(self, use_dump):
        result = self._do_dump_test(CONNECT +
b"""
@create Foo
@set Foo=_/foo/bar/baz:test
@set Foo=:clear
""",b"""
ex Foo=/
""", use_dump=use_dump)
        self.assertTrue(b'0 propert' in result)

    def test_clear_nodump(self):
        self._test_clear(use_dump=False)

    def test_clear_dump(self):
        self._test_clear(use_dump=True)

    def test_clear_priv(self):
        result_setup= self._do_full_session(CONNECT +
b"""
@pcreate TestUser=foo
@create Foo
@set Foo=~specialprop:foobar
@set Foo=_not/~special:bazquux
@chown Foo=TestUser
drop Foo
""")
        result = self._do_full_session(b"""
connect TestUser foo
@set Foo=:clear
ex Foo=/
""")
        self.assertTrue(b'1 propert' in result)
        self.assertTrue(b'~specialprop' in result)

class TestUnbless(ServerTestBase):
    def test_simple(self):
        result = self._do_full_session(CONNECT +
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
        result = self._do_full_session(CONNECT +
b"""
@pcreate Foo=pass
@force Foo=@create Bar
ex #3
""")
        self.assertTrue(b'Owner: Foo' in result)

    def test_as_player_force_zombie(self):
        result_setup = self._do_full_session(CONNECT +
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
        result_setup = self._do_full_session(CONNECT +
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
