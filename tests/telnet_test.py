#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\r\n"
IAC = b"\xFF"
DONT = b"\xFE"
DO = b"\xFD"
WONT = b"\xFC"
WILL = b"\xFB"
SB = b"\xFA"
GA = b"\xF9"
EL = b"\xF8"
EC = b"\xF7"
AYT = b"\xF6"
AO = b"\xF5"
IP = b"\xF4"
BRK = b"\xF3"
DM = b"\xF2"
NOP = b"\xF1"
SE = b"\xF0"


class TestTelnetTrivial(ServerTestBase):
    @asyncio.coroutine
    def _session(self, reader, writer):
        mcp = yield from reader.readline()
        self.assertTrue(b"mcp" in mcp)
        welcome = yield from reader.readline()
        self.assertEqual(b"### EMPTY WELCOME FILE ###\r\n", welcome)
        writer.write(IAC + WILL + b"\x01") # echo option
        reply = yield from reader.readexactly(3)
        self.assertEqual(reply, IAC + DONT + b"\x01")

    def test(self):
       self._do_full_session_interactive(self._session)
        
class TestTelnetMultiOption(ServerTestBase):
    @asyncio.coroutine
    def _session(self, reader, writer):
        mcp = yield from reader.readline()
        self.assertTrue(b"mcp" in mcp)
        welcome = yield from reader.readline()
        self.assertEqual(b"### EMPTY WELCOME FILE ###\r\n", welcome)
        writer.write(IAC + WILL + b"\x01" +
                     IAC + DO + b"\x01") 
        reply = yield from reader.readexactly(6)
        self.assertEqual(reply, IAC + DONT + b"\x01" + IAC + WONT + b"\x01")

    def test(self):
       self._do_full_session_interactive(self._session)

class TestTelnetMultiOptionBusy(ServerTestBase):
    extra_params = {'command_burst_size': '10000', 'commands_per_time': 1000,
                    'max_output': 10000, 'command_time_msec': '1',}
    @asyncio.coroutine
    def _session(self, reader, writer):
        mcp = yield from reader.readline()
        self.assertTrue(b"mcp" in mcp)
        welcome = yield from reader.readline()
        self.assertEqual(b"### EMPTY WELCOME FILE ###\r\n", welcome)
        writer.write(CONNECT)
        motd = yield from reader.readline()
        room_name = yield from reader.readline()
        room_desc = yield from reader.readline()
        muf_program = b": main\r\n" + (b"  1\r\n" * 450) + b";\r\n"
        writer.write(b"@program test.muf\r\n\r\ni\r\n" + muf_program + b"\r\n.\r\nq\r\n")
        line = ""
        while line != b"Editor exited.\r\n":
            line = yield from reader.readline()
        writer.write(b"@list test.muf\r\n" + IAC + WILL + b"\x01" +
                     IAC + DO + b"\x01") 
        text = b""
        while DONT not in text and WONT not in text and b"lines displayed." not in text:
            text += yield from reader.readline()
            logging.debug('text = %s', text)
        self.assertTrue(IAC + DONT + b"\x01" in text)
        self.assertTrue(IAC + WONT + b"\x01" in text)
        self.assertTrue(text.index(IAC + DONT + b"\x01") < text.index(IAC + WONT + b"\x01"))
        writer.close()

    def test(self):
       self._do_full_session_interactive(self._session, timeout=60)
        
        

class TestTelnetTrivialNoSSL(TestTelnetTrivial):
    use_ssl = False

class TestConnectMultiOptionNoSSL(TestTelnetMultiOption):
    use_ssl = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
