#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase, MPITestBase

CONNECT = b"connect One potrzebie\n"

class TestBlankAction(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo;foobar=me
@link foo=me
@lock foo=me&!me
@fail foo=Triggered failure message cmd="{&cmd}" arg="{&arg}"
@succ foo=Triggered success message.
@set foo=H
foo Arguments here
foobar More arguments here
""")
        self.assertTrue(b'Triggered failure message cmd="foo" arg="Arguments here"' in result)
        self.assertTrue(b'Triggered failure message cmd="foobar" arg="More arguments here"' in result)

class TestBlankActionSpecialName(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo;say;pose;delimiter=me
@link foo=me
@lock foo=me&!me
@fail foo=Triggered failure message cmd="{&cmd}" arg="{&arg}"
@succ foo=Triggered success message.
@set foo=H
"As say.
:As pose.
;As delimiter.
@name foo=foo
""")
        self.assertTrue(b'Triggered failure message cmd="say" arg="As say."' in result)
        self.assertTrue(b'Triggered failure message cmd="pose" arg="As pose."' in result)
        self.assertTrue(b'Triggered failure message cmd="delimiter" arg="As delimiter."' in result)

class TestMPIOverflow(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT +
b"""!@action foo=me
@link foo=me
@lock foo=me&!me
@fail foo={exec:_/fl}
@set foo=H
foo 
""")
        self.assertTrue(b' Recursion limit exceeded.' in result)

class TestForceOverflow(ServerTestBase):
    def test(self):
        result1 = self._do_full_session(CONNECT +
b"""
@pcreate TestPlayer=test
@action foo=here
@link foo=here
@lock foo=me&!me
@fail foo={force:*TestPlayer,foo}
@bless foo=_/fl
@set foo=H
""")
        result2 = self._do_full_session(
b"""connect TestPlayer test
foo 
""")
        self.assertTrue(b"You can't force recursively" in result2)

class TestMPILockOverflow(ServerTestBase):
    def test(self):
        result1 = self._do_full_session(CONNECT +
b"""
@action foo=here
@link foo=here
@lock foo=_fooprop:42
@set foo=_fooprop:{if:{locked:me,#2},42,0}
@succ foo=Foo success.
@fail foo=Foo failure.
foo
""")
        logging.error("result1 = %s", result1);
        self.assertTrue(b'Foo failure.' in result1)


class TestParseErrors(MPITestBase):
    def test_bad_escape(self):
        result = self._test_mpi(rb"{le:rgo,\\", pass_check=False)
        self.assertTrue(b'End brace not found' in result)
    
    def test_bad_escape_2(self):
        result = self._test_mpi(rb"{filter:b,a,in`valid}}}", pass_check=False)
        self.assertTrue(b'End brace not found' in result)

    def test_bad_while(self):
        result = self._test_mpi(rb"{NULL:{WHILE:1,{NULL:x}{NULL}{NULL:{NULL:{NULL}}}}}}}}}}}}}}", pass_check=False)
        self.assertTrue(b'Instruction limit exceeded' in result)

class TestTime(MPITestBase):
    def test_ftime_sanity(self):
        result = self._test_mpi(rb"{null:{FTIME:%a,,100000000000000000}}Test passed.", pass_check=False)
        self.assertTrue(b'Out of range time' in result or b'Test passed.' in result)

class TestFunc(MPITestBase):
    def test_threearg(self):
        self._test_mpi(rb"{func:foo,va,vb,vc,func({&va}:{&vb}:{&vc})}"
                      +rb"{if:{eq:{foo:x,y,z},func(x:y:z)},Test passed.}")

    def test_v(self):
        self._test_mpi(rb"{func:foo,va,vb,vc,func({v:va}:{v:vb}:{v:vc})}"
                      +rb"{if:{eq:{foo:x,y,z},func(x:y:z)},Test passed.}")

    def test_set(self):
        self._test_mpi(rb"{func:foo,va,vb,vc,{null:{set:va,quux}}func({v:va}:{v:vb}:{v:vc})}"
                      +rb"{if:{eq:{foo:x,y,z},func(quux:y:z)},Test passed.}")
    
    def test_func_loop(self):
        result = self._test_mpi(rb"{while:1,{func:x,}}", pass_check=False)
        self.assertTrue(b"Too many functions" in result)


class TestProp(MPITestBase):
    def test_direct(self):
        self._test_mpi(rb"{if:{eq:{prop:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:testvalue
""")
    
    def test_direct_exact(self):
        self._test_mpi(rb"{if:{eq:{prop!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:testvalue
""")

    def test_env(self):
        self._test_mpi(rb"{if:{eq:{prop:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:testvalue
""")

    def test_noenv(self):
        self._test_mpi(rb"{if:{ne:{prop!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:testvalue
""")

    def test_env_exec(self):
        self._test_mpi(rb"{if:{eq:{exec:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:test{null:42}value
""")

    def test_direct_exec(self):
        self._test_mpi(rb"{if:{eq:{exec:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:test{null:42}value
""")
    
    def test_noenv_exec(self):
        self._test_mpi(rb"{if:{ne:{exec!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:testvalue
""")

    def test_index(self):
        self._test_mpi(rb"{if:{eq:{index:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:_testprop2
@set runtest=_testprop2:testvalue
""")

    def test_index_direct(self):
        self._test_mpi(rb"{if:{eq:{index!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set runtest=_testprop:_testprop2
@set runtest=_testprop2:testvalue
""")

    def test_index_noenv(self):
        self._test_mpi(rb"{if:{ne:{index!:_testprop},testvalue},Test passed.}",
            before=rb"""
@set #0=_testprop:_testprop2
@set #0=_testprop2:testvalue
""")

    def test_propdir(self):
        self._test_mpi(rb"{if:{propdir:_testprop},Test passed.}",
            before=rb"""
@set runtest=_testprop/foo:yes
""")

    def test_listprops(self):
        self._test_mpi(rb"{if:{eq:{listprops:_testprop},_testprop/bar\r_testprop/foo},Test passed.}",
            before=rb"""
@set runtest=_testprop/foo:1
@set runtest=_testprop/bar:2
""")

    def test_listprops_overflow(self):
        set_commands = rb""
        for i in range(200):
            set_commands += rb"@set runtest=_testprop/verlongnameAAAAAAAAAAAAAAAAAAAAAA" + str(i).encode() + b":1\n"
        self._test_mpi(rb"{if:{listprops:_testprop},Test passed.}",
            before=set_commands)

    def test_concat_simple(self):
        self._test_mpi(rb"{if:{eq:{concat:_testprop},foo bar baz},Test passed.}",
            before=rb"""
@set runtest=_testprop#:3
@set runtest=_testprop#/1:foo
@set runtest=_testprop#/2:bar
@set runtest=_testprop#/3:baz
""")

    def test_select_example(self):
        self._test_mpi(rb"{if:{eq:{select:9,_testprop}/{select:16,_testprop}/{select:25,_testprop},two/three/four},Test passed.}",
            before=rb"""
@set runtest=_testprop#:20
@set runtest=_testprop#/1:one
@set runtest=_testprop#/5:two
@set runtest=_testprop#/16:three
@set runtest=_testprop#/20:four
""")

    def test_list(self):
        self._test_mpi(rb"{if:{eq:{list:_testprop},foo\rbar\rbaz},Test passed.}",
            before=rb"""
@set runtest=_testprop#:3
@set runtest=_testprop#/1:foo
@set runtest=_testprop#/2:bar
@set runtest=_testprop#/3:baz
""")

    def test_lexec(self):
        self._test_mpi(rb"{if:{eq:{lexec:_testprop},foo /bar/baz},Test passed.}",
            before=rb"""
@set runtest=_testprop#:3
@set runtest=_testprop#/1: {prop!:_other} / 
@set runtest=_testprop#/2:{null:x}bar
@set runtest=_testprop#/3:/ba{null:..}z
@set runtest=_other:foo
""")

    def test_rand(self):
        self._test_mpi(rb"{if:{eq:{rand:_testprop},foo},Test passed.}",
            before=rb"""
@set runtest=_testprop#:3
@set runtest=_testprop#/1:{prop!:_other}
@set runtest=_testprop#/2:{prop!:_other}
@set runtest=_testprop#/3:{prop!:_other}
@set runtest=_other:foo
""")


class TestString(MPITestBase):
    def test_nl(self):
        self._test_mpi(rb"{if:{eq:{nl},\r},Test passed.}")
    
    def test_lit(self):
        self._test_mpi(rb"{if:{eq:{lit:{nl}},\{nl\}},Test passed.}")

    def test_eval(self):
        self._test_mpi(rb"{if:{eq:{eval:\{prop:_testprop\}},foo},Test passed.}",
            before=rb"""
@set runtest=_testprop:foo
""")

    def test_evalbang(self):
        self._test_mpi(rb"{if:{eq:{eval!:\{prop:@testprop\}},foo},Test passed.}", 
            blessed=True,
            before=rb"""
@set runtest=@testprop:foo
""")

    def test_eval_nopriv(self):
        result = self._test_mpi(rb"{eval:\{prop:@testprop\}}", 
            blessed=True,
            pass_check=False,
            before=rb"""
@set runtest=@testprop:foo
""")
        self.assertTrue(b'Permission denied.' in result)


    def test_strip(self):
        self._test_mpi(rb"{if:{eq:{strip:   foo   \r   },foo},Test passed.}")

    def test_mklist(self):
        self._test_mpi(rb"{if:{eq:{mklist:foo,bar,baz},foo\rbar\rbaz},Test passed.}")

    def test_pronouns_simple(self):
        self._test_mpi(rb"{if:{eq:{pronouns:%n's},One's},Test passed.}")

    def test_left_simple(self):
        self._test_mpi(rb"{if:{eq:{left:Hello,10,_.},Hello_._._},Test passed.}")

    def test_right_simple(self):
        self._test_mpi(rb"{if:{eq:{right:Hello,10,_.},_._._Hello},Test passed.}")

    def test_center_simple(self):
        self._test_mpi(rb"{if:{eq:{center:Hello,11,_.},_._Hello_._},Test passed.}")

    def test_sublist(self):
        self._test_mpi(rb"{if:{eq:{sublist:foo/x//bar/y//quux/z//blaz,2,3,//},bar/y//quux/z},Test passed.}")


class TestList(MPITestBase):    
    def test_count(self):
        self._test_mpi(rb"{if:{eq:{count:xyz}/{count:foo\rbar\r\rbaz},1/4},Test passed.}")
 
    def test_fold_simple(self):
        self._test_mpi(rb"{if:{eq:{fold:x,y,foo\rbar\rbaz,*{&x}::{&y}},**foo::bar::baz},Test passed.}")
    
    def test_filter(self):
        self._test_mpi(rb"{if:{eq:{filter:x,foo/x//bar/y//baz,{smatch:{&x},b*},//},bar/y//baz},Test passed.}")
    
    def test_lremove(self):
        self._test_mpi(rb"{if:{eq:{lremove:foo\rbar\rbaz\rquux\rquux\rbar,baz\rquux\rnotin},foo\rbar},Test passed.}")

    def test_lcommon(self):
        self._test_mpi(rb"{if:{eq:{lcommon:foo\rbar\rbaz\rquux\rquux\rbar,baz\rquux\rnotin},baz\rquux},Test passed.}")

    def test_lunion(self):
        self._test_mpi(rb"{if:{eq:{lunion:foo\rbar\rbaz\rquux\rquux\rbar,baz\rquux\rnotin},foo\rbar\rbaz\rquux\rnotin},Test passed.}")

    def test_lsort_simple(self):
        self._test_mpi(rb"{if:{eq:{lsort:foo\rbar\rbaz\rquux\rquux\rbar\rbaz\rquux\rnotin},bar\rbar\rbaz\rbaz\rfoo\rnotin\rquux\rquux\rquux},Test passed.}")
    
    def test_lsort_func(self):
        self._test_mpi(rb"{if:{eq:{lsort:-1\r3\r4,x,y,{lt:{abs:{subt:{&x},2}},{abs:{subt:{&y},2}}}},-1\r4\r3},Test passed.}")

    def test_lunique_simple(self):
        self._test_mpi(rb"{if:{eq:{lunique:foo\rbar\rbaz\rquux\rquux\rbar\rbaz\rquux\rnotin},foo\rbar\rbaz\rquux\rnotin},Test passed.}")
 
class TestCompare(MPITestBase):
    def test_eq(self):
        self._test_mpi(rb"{if:{and:{eq:42,00042},{eq:FOO,foo},{not:{eq:42,43}},{not:{eq:f,42}}},Test passed.}")

    def test_ne(self):
        self._test_mpi(rb"{if:{and:{not:{ne:42,00042}},{not:{ne:FOO,foo}},{ne:42,43},{ne:f,42}},Test passed.}")

    def test_lt(self):
        self._test_mpi(rb"{if:{and:{lt:42,0043},{lt:abc,def},{not:{lt:42,00042}}},Test passed.}")

    def test_le(self):
        self._test_mpi(rb"{if:{and:{le:42,0043},{le:abc,def},{le:42,00042}},Test passed.}")

    def test_gt(self):
        self._test_mpi(rb"{if:{and:{gt:43,0042},{gt:def,abc},{not:{gt:42,00042}}},Test passed.}")

    def test_ge(self):
        self._test_mpi(rb"{if:{and:{ge:43,0042},{ge:def,abc},{ge:42,00042}},Test passed.}")

    def test_min_simple1(self):
        self._test_mpi(rb"{if:{eq:{min:00041,42},00041},Test passed.}")

    def test_min_simple2(self):
        self._test_mpi(rb"{if:{eq:{min:def,abc},abc},Test passed.}")
    
    def test_max_simple1(self):
        self._test_mpi(rb"{if:{eq:{max:00041,42},42},Test passed.}")

    def test_max_simple2(self):
        self._test_mpi(rb"{if:{eq:{max:def,abc},def},Test passed.}")

    def test_isnum(self):
        self._test_mpi(rb"{if:{and:{isnum:42},{isnum:-42},{not:{isnum:abc}},{not:{isnum:42a}}},Test passed.}")
    
    def test_isdbref(self):
        self._test_mpi(rb"{if:{and:{isdbref:#2},{isdbref:#0},{not:{isdbref:#-1}},{not:{isdbref:One}}},Test passed.}")

    def test_or(self):
        self._test_mpi(rb"{if:{and:{or:0,0,0,{null:{store:a,_one}},1,{store:b,_two}},{eq:{prop:_one}{prop:_two},a}},Test passed.}")

    def test_xor(self):
        self._test_mpi(rb"{if:{and:{xor:1,0},{not:{xor:1,1}},{xor:0,1},{not:{xor:0,0}}},Test passed.}")

    def test_default(self):
        self._test_mpi(rb"{default:,Test}{default:0, }{default:passed,not passed}.")

    def test_while(self):
        self._test_mpi(rb"{null:{with:x,10,{while:{ne:{&x},0},{store:{&x},_testprop#/{&x}}{dec:x}}{store:10,_testprop#}}}"
                     + rb"{if:{eq:{concat:_testprop},1 2 3 4 5 6 7 8 9 10},Test passed.}")
    
    def test_for(self):
        self._test_mpi(rb"{null:{for:x,10,1,-1,{store:{&x},_testprop#/{&x}}{dec:x}}{store:10,_testprop#}}"
                     + rb"{if:{eq:{concat:_testprop},1 2 3 4 5 6 7 8 9 10},Test passed.}")

    def test_foreach(self):
        self._test_mpi(rb"{null:{foreach:x,1\r2\r3\r4\r5\r6\r7\r8\r9\r10,{store:{&x},_testprop#/{&x}}{dec:x}}{store:10,_testprop#}}"
                     + rb"{if:{eq:{concat:_testprop},1 2 3 4 5 6 7 8 9 10},Test passed.}")

class TestMath(MPITestBase):
    def test_incdec(self):
        self._test_mpi(rb"{with:var,42,{null:{inc:var}{dec:var}{dec:var}},{if:{eq:{&var},41},Test passed.}}")

    def test_add(self):
        self._test_mpi(rb"{if:{eq:{add:20,19,5,-2},42},Test passed.}")

    def test_subt(self):
        self._test_mpi(rb"{if:{eq:{subt:20,19,5,-2},-2},Test passed.}")

    def test_mult(self):
        self._test_mpi(rb"{if:{eq:{mult:20,19,5,-2},-3800},Test passed.}")

    def test_div(self):
        self._test_mpi(rb"{if:{eq:{div:20000,19,5,-2},-105},Test passed.}")

    def test_div_overflow(self):
        self._test_mpi(rb"{null:{div:-2147483648,-1}}Test passed.")

    def test_div_zero(self):
        self._test_mpi(rb"{null:{div:10,0}}Test passed.")

    def test_mod(self):
        self._test_mpi(rb"{if:{eq:{mod:20000,19,5,3},2},Test passed.}")

    def test_mod_overflow(self):
        self._test_mpi(rb"{null:{mod:-2147483648,-1}}Test passed.")

    def test_mod_zero(self):
        self._test_mpi(rb"{null:{mod:10,0}}Test passed.")

    def test_abs(self):
        self._test_mpi(rb"{if:{eq:{abs:-0042}/{abs:42}/{abs:0},42/42/0},Test passed.}")

    def test_sign(self):
        self._test_mpi(rb"{if:{eq:{sign:-0042}/{sign:42}/{sign:0},-1/1/0},Test passed.}")

    def test_dist(self):
        self._test_mpi(rb"{if:{eq:{dist:0,2}/{dist:4,0}/{dist:3,4}/{dist:1,7,4,11}/{dist:1,7,-1,2,8,0},2/4/5/5/2},Test passed.}")

class TestConnect(MPITestBase):    
    def test_ontime(self):
        self._test_mpi(rb"{if:{gt:{ontime:me},-1},Test passed.}")

    def test_idle(self):
        self._test_mpi(rb"{if:{gt:{idle:me},-1},Test passed.}")
    
    def test_online_one(self):
        self._test_mpi(rb"{online}{nl}{if:{eq:{online},*One},Test passed.}", blessed=True)


class TestDB(MPITestBase):
    def test_contains_nested(self):
        self._test_mpi(rb"{if:{and:{contains:$bar,$foo},{contains:$bar,me},{not:{contains:$foo,$bar}}},Test passed.}",
            before=rb"""
@create Foo
@propset me=dbref:_reg/foo:Foo
@create Bar
@propset me=dbref:_reg/bar:Bar
@conlock Foo=me
put Bar=Foo
""")

    def test_holds_nested(self):
        self._test_mpi(rb"{if:{and:{holds:$bar,$foo},{not:{holds:$bar,me}},{not:{contains:$foo,$bar}}},Test passed.}",
            before=rb"""
@create Foo
@propset me=dbref:_reg/foo:Foo
@create Bar
@propset me=dbref:_reg/bar:Bar
@conlock Foo=me
put Bar=Foo
""")

    def test_dbeq_simple(self):
        self._test_mpi(rb"{if:{and:{dbeq:#1,One},{dbeq:#1,*One},{dbeq:#1,#1},{not:{dbeq:me,here}}},Test passed.}")

    def test_loc(self):
        self._test_mpi(rb"{if:{and:{dbeq:{loc:$bar},$foo},{dbeq:{loc:$foo},me},{dbeq:{loc:me},#0}},Test passed.}",
            before=rb"""
@create Foo
@propset me=dbref:_reg/foo:Foo
@create Bar
@propset me=dbref:_reg/bar:Bar
@conlock Foo=me
put Bar=Foo
""")

    def test_nearby(self):
        self._test_mpi(rb"{if:{and:{nearby:$quux,me},{nearby:$baz,$foo},{not:{nearby:$foo,$quux}},{not:{nearby:me,$bar}}},Test passed.}",
            before=rb"""
@create Foo
@propset me=dbref:_reg/foo:Foo
@create Bar
@propset me=dbref:_reg/bar:Bar
@conlock Foo=me
@create Quux
@propset me=dbref:_reg/quux:Quux
@create Baz
@propset me=dbref:_reg/baz:Baz
drop Quux
put Bar=Foo
""")

    def test_flags_simple(self):
        self._test_mpi(rb"{if:{eq:{flags:me},PWM3},Test passed.}")

    def test_tell_simple(self):
        self._test_mpi(rb"{null:{tell:Test passed.,me}}Not test pass output.")

    def test_otell_simple_noprefix(self):
        self._test_mpi(rb"{null:{otell:Test passed.,here,#-1}}Not test pass output.")

    def test_owner(self):
        self._test_mpi(rb"{if:{eq:{owner:Foo}/{owner:TestUser}/{owner:Bar},*One/*TestUser/*TestUser},Test passed.}",
            before=rb"""
@pcreate TestUser=foo
@create Foo
@create Bar
@chown Bar=Testuser
""")

    def test_links_simple(self):
        self._test_mpi(rb"{if:{eq:{links:me}/{links:test}/{links:foo},#0/{ref:Foo}/*One},Test passed.}",
            before=rb"""
@act test=here
@create Foo
@link foo=me
@link test=foo
""")

    def test_contents_simple(self):
        self._test_mpi(rb"{if:{eq:{contents:here,player}/{contents:here,thing}/{contents:here,program},*One/{ref:Quux}\r{ref:Foo}/{ref:test.muf}},Test passed.}",
            before=rb"""
@create Foo
@create Quux
drop foo
drop quux
@program test.muf
q
drop test.muf
""")
    def test_exits_simple(self):
        self._test_mpi(rb"{if:{eq:{exits:here},{ref:bar}\r{ref:foo}\r{ref:runtest}},Test passed.}",
            before=rb"""
@act foo=here
@act bar=here
""")

    def test_links_simple(self):
        self._test_mpi(rb"{if:{eq:{controls:Foo,TestUser}/{controls:TestUser,TestUser}/{controls:Bar,TestUser}/{controls:Foo,Bar},0/1/1/0},Test passed.}",
            before=rb"""
@pcreate TestUser=foo
@create Foo
@create Bar
@chown Bar=Testuser
""")

    def test_locked(self):
        self._test_mpi(rb"{if:{and:{locked:me,Foo},{not:{locked:TestUser,Foo}}},Test passed.}",
            before=rb"""
@pcreate TestUser=foo
@create Foo
@lock Foo=TestUser
""")

    def test_testlock_invalid(self):
        result = self._test_mpi(rb"{testlock:,,}", pass_check=False)
        self.assertTrue(b"failed" in result)

    def test_testlock_invalid2(self):
        result = self._test_mpi(rb"{testlock:,,#-7}", pass_check=False)
        self.assertTrue(b"failed" in result)

    def test_testlock(self):
        result = self._test_mpi(rb"{if:{and:{not:{testlock:Foo,_testprop,me}},{testlock:Foo,_testprop,*TestUser}},Test passed.}",
            before=rb"""
@create Foo
@pcreate TestUser=xxx
@propset foo=lock:_testprop:TestUser
""")

    def test_name_simple(self):
        self._test_mpi(rb"{if:{eq:{name:me}/{name:here}/{name:testthing2},One/Room Zero/testthing},Test passed.}", before=rb"""
@act testthing;testthing2=here
""")

    def test_fullname_simple(self):
        self._test_mpi(rb"{if:{eq:{fullname:me}/{fullname:here}/{fullname:testthing2},One/Room Zero/testthing;testthing2},Test passed.}", before=rb"""
@act testthing;testthing2=here
""")



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
