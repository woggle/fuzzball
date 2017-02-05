#!/usr/bin/env python3.6
import asyncio
import logging
import re
import time
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

@asyncio.coroutine
def write_quit_after(delay, writer):
    yield from asyncio.sleep(delay)
    writer.write(b"QUIT\r\n")


class TestConnectHugeMuf(ServerTestBase):
    repeat_count = 200
    line_count = 10000
    quit_delay = 30 
    expect_no_truncate = True 
    extra_params = {'command_burst_size': '1000000', 'commands_per_time': 100000,
                    'max_output': 10000 * 500 * 20}
    def test_huge_muf(self):
        muf_program = b": main \n" + b"  1\n" * self.line_count + b";\n"
        string = (CONNECT + 
b"""@program test.muf
i
""" + muf_program + b"\n\n" +
b""".
c
q
""" + (b"@list test.muf\n" * self.repeat_count) + 
b"""
say Got here
""")
        string = string.replace(b"\n", b"\r\n")
        def input_func(writer):
            writer.write(string)
            asyncio.ensure_future(write_quit_after(self.quit_delay, writer))
        result = self._do_full_session_timed_output(input_func, timeout=300)
        #logging.debug('result = %s', result)
        self.assertTrue(
            b"### EMPTY WELCOME FILE ###" in result
        )
        #logging.debug('raw result is <%s>', result)
        self.assertTrue(
            b": main" in result
        )
        self.assertTrue(
            b": main" in result
        )
        if self.expect_no_truncate:
            self.assertEqual(
                result.count(b": main"), self.repeat_count
            )
            self.assertTrue(
                b"Got here" in result
            )
            self.assertTrue(
                b"Come back later!" in result
            )

class TestConnectHugeMufNoSSL(TestConnectHugeMuf):
    use_ssl = False

class TestConnectHugeMufTruncate(TestConnectHugeMuf):
    quit_delay = 0
    line_count = 10000
    repeat_count = 500
    expect_no_truncate = False
    extra_params = {'command_burst_size': '1000000', 'commands_per_time': 100000,
                    'max_output': 10000 * 100}

class TestConnectHugeMufTruncateNoSSL(TestConnectHugeMuf):
    quit_delay = 0
    line_count = 10000
    repeat_count = 500
    expect_no_truncate = False
    extra_params = {'command_burst_size': '1000000', 'commands_per_time': 100000,
                    'max_output': 10000 * 100}

class TestConnectHugeMufWait(ServerTestBase):
    extra_params = {'command_burst_size': '10000', 'commands_per_time': 1000,
                    'max_output': 100000, 'command_time_msec': '1',}
    line_count = 10000
    repeat_count = 50
    @asyncio.coroutine
    def _session(self, reader, writer):
        stdin_reader = asyncio.StreamReader()
        stdin_reader_protocol = asyncio.StreamReaderProtocol(reader)
        wait_line = yield from stdin_reader.readline()
        logging.debug('got line %s', wait_line)
        mcp = yield from reader.readline()
        self.assertTrue(b"mcp" in mcp)
        welcome = yield from reader.readline()
        self.assertEqual(b"### EMPTY WELCOME FILE ###\r\n", welcome)
        logging.debug('got welcome')
        writer.write(CONNECT)
        motd = yield from reader.readline()
        room_name = yield from reader.readline()
        room_desc = yield from reader.readline()
        muf_program = b": main\r\n" + (b"  1\r\n" * self.line_count) + b";\r\n"
        writer.write(b"@program test.muf\r\n\r\ni\r\n" + muf_program + b"\r\n.\r\nq\r\n")
        line = ""
        while line != b"Editor exited.\r\n":
            line = yield from reader.readline()
        writer.write(b"@list test.muf\r\n" * self.repeat_count)
        saw_flush = False
        saw_count = 0
        timed_out = False
        num_lines = 0
        while not timed_out and saw_count < self.repeat_count:
            try:
                next_line_future = asyncio.ensure_future(reader.readline())
                line = yield from asyncio.wait_for(next_line_future, timeout=1)
                #logging.debug('got line <%s> @ %.2f', line, time.time())
                next_line_future = None
                if b"<Output Flushed>" in line:
                    logging.debug('saw flush');
                    saw_flush = True
                if b" lines displayed." in line:
                    logging.debug('saw count');
                    saw_count += 1
                num_lines += 1
            except asyncio.TimeoutError:
                logging.debug('saw timeout')
                timed_out = True
                break
        self.assertTrue(saw_flush or saw_count == self.repeat_count)
        logging.debug('trying quit')
        writer.write(b"QUIT\r\n")
        if timed_out:
            empty = yield from next_line_future
        else:
            empty = yield from reader.readline()
        bye_message = yield from reader.readline()
        empty = yield from reader.readline()
        self.assertTrue(b"Come back later!" in bye_message)
        writer.close()
        
    def test_huge_muf(self):
        self._do_full_session_interactive(self._session, timeout=600)

class TestConnectHugeMufWaitNoSSL(TestConnectHugeMufWait):
    use_ssl = False

class TestConnectHugeMufWaitBigOutput(TestConnectHugeMufWait):
    extra_params = {'command_burst_size': '10000', 'commands_per_time': 1000,
                    'max_output': 10000 * 100 * 5, 'command_time_msec': '1',}

class TestConnectHugeMufWaitBigOutputNoSSL(TestConnectHugeMufWaitBigOutput):
    use_ssl = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
