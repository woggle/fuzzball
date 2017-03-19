import asyncio
import logging
import os
import os.path
import signal
import socket
import ssl
import sys
import tempfile
import threading
import time
import unittest

SOURCE_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

MINIMAL_DB_PATH = 'game/data/minimal.db'
SERVER_PATH = 'src/fbmuck'
RESOLVER_PATH = 'src/fb-resolver'
TEST_PORT = 35434
TEST_SSL_PORT = 35435

CONNECT_GOD = b"connect One potrzebie\n"
CONNECT_CREATE_TEST_USER = CONNECT_GOD + rb"""
@pcreate TestUser=testpassword
"""
CONNECT_TEST_USER = rb"""
connect TestUser testpassword
"""
BOOT_TEST_USER = rb"""
@boot TestUser
"""

cached_server_options = None
@asyncio.coroutine
def get_server_options():
    global cached_server_options
    if cached_server_options == None:
        # use event loop for this to avoid disrupting SIGCHLD
        process = yield from asyncio.create_subprocess_exec(
            os.path.join(SOURCE_ROOT_DIR, SERVER_PATH),
             '-compileoptions',
             stdin=asyncio.subprocess.DEVNULL,
             stdout=asyncio.subprocess.PIPE,
             stderr=asyncio.subprocess.DEVNULL,
        )
        options_string, _ = yield from process.communicate()
        cached_server_options = set(map(lambda b: b.decode(), options_string.split(b" ")))
    return cached_server_options

class Server(object):
    def __init__(self, input_database=None, params={}, normal_port=TEST_PORT, ssl_port=TEST_SSL_PORT,
                 game_dir=None, timezone=None):
        self.input_database = input_database
        if not self.input_database:
            self.input_database = os.path.join(SOURCE_ROOT_DIR, MINIMAL_DB_PATH)
        self.temp_dir = tempfile.TemporaryDirectory()
        if game_dir:
            self.game_dir = game_dir
        else:
            self.game_dir = self.temp_dir.name
        self.normal_port = normal_port
        self.ssl_port = ssl_port
        self.params = params
        self.timezone = timezone
        assert(self.normal_port and self.ssl_port)

    @asyncio.coroutine
    def _asyncio_run_simple(self, command_line):
        process = \
            yield from asyncio.create_subprocess_exec(*command_line, cwd=self.game_dir,
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                stdin=asyncio.subprocess.DEVNULL)
        return_code = yield from process.wait()
        if return_code != 0:
            raise OSError("command %s failed" % (command_line))

    @asyncio.coroutine
    def _generate_certificate(self):
        yield from self._asyncio_run_simple([
            'openssl', 'ecparam', 
            '-name', 'secp256r1', '-out', 'ecparam.pem',
        ])
        yield from self._asyncio_run_simple([
            'openssl', 'req', '-new', 
            '-newkey', 'ec:ecparam.pem',
            '-nodes', '-x509',
            '-subj', '/CN=TESTMUCK',
            '-keyout', 'server.key',
            '-out', 'server.pem',
        ])

    def _generate_empty_motd(self):
        with open(os.path.join(self.game_dir, 'motd.txt'), 'w') as fh:
            fh.write("### EMPTY MOTD FILE ###\n")

    def _generate_empty_welcome(self):
        with open(os.path.join(self.game_dir, 'welcome.txt'), 'w') as fh:
            fh.write("### EMPTY WELCOME FILE ###\n")

    @asyncio.coroutine 
    def _generate_parmfile(self):
        yield from self._generate_certificate()
        self._generate_empty_motd()
        self._generate_empty_welcome()
        try:
            os.makedirs(os.path.join(self.game_dir, 'logs'))
        except:
            pass
        try:
            os.makedirs(os.path.join(self.game_dir, 'muf'))
        except:
            pass
        with open(os.path.join(self.game_dir, 'test_parm_file'), 'w') as fh:
            fh.write("ssl_cert_file=server.pem\nssl_key_file=server.key\nfile_motd=motd.txt\nfile_welcome_screen=welcome.txt\n")
            for key, value in self.params.items():
                fh.write("{key}={value}\n".format(key=key, value=value))
            fh.close()
    
    @asyncio.coroutine
    def _forward_stdout(self):
        while True:
            data = yield from self.process.stdout.readline()
            if len(data) == 0:
                break
            sys.stdout.write(data.decode())
    
    @asyncio.coroutine
    def _forward_stderr(self):
        while True:
            data = yield from self.process.stderr.readline()
            if len(data) == 0:
                break
            sys.stdout.write(data.decode())

    def set_output_to_input(self):
        os.rename(os.path.join(self.game_dir, 'dbout'), os.path.join(self.game_dir, 'dbin'))
        self.input_database = os.path.join(self.game_dir, 'dbin')

    @asyncio.coroutine
    def start(self):
        logging.info('start(%s)', self.game_dir)
        yield from self._generate_parmfile()
        command_line = [
           os.path.join(SOURCE_ROOT_DIR, SERVER_PATH),
           '-dbin', self.input_database,
           '-gamedir', self.game_dir,
           '-dbout', os.path.join(self.game_dir, 'dbout'),
           '-port', str(self.normal_port),
           '-bindv4', '127.0.0.1',
           '-ipv4',
           '-nodetach',
           '-parmfile', 'test_parm_file',
        ]
        options = yield from get_server_options()
        if 'IPV6' in options:
            command_line += ['-ipv6', '-bindv6', '::1']
        if 'RESOLVER' in options:
            command_line += ['-resolver', os.path.join(SOURCE_ROOT_DIR, RESOLVER_PATH)]
        if 'SSL' in options:
            command_line += ['-sport', str(self.ssl_port)]

        logging.debug('server command line is %s', command_line)
        my_env = os.environ.copy()
        if self.timezone:
            my_env['TZ'] = self.timezone
        self.process = \
            yield from asyncio.create_subprocess_exec(*command_line, cwd=self.game_dir,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=my_env)
        self.forward_stdout = asyncio.ensure_future(self._forward_stdout())
        self.forward_stderr = asyncio.ensure_future(self._forward_stderr())
        self.process_wait = asyncio.ensure_future(self.process.wait())
        yield from asyncio.sleep(0.2) # wait for server to bind, etc.

    def _stop(self, timeout):
        logging.info('about to SIGTERM to %d', self.process.pid)
        try:
            self.process.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            logging.info('already dead?')
            pass
        logging.info('about to start wait')
        wait_future = self.process_wait
        done, pending = yield from asyncio.wait([wait_future], timeout=timeout)
        logging.info('tried waiting')
        if len(done) == 0:
            logging.error('normal shutdown failed')
            self.process.send_signal(signal.SIGKILL)
            done, pending = yield from asyncio.wait([wait_future])
            assert(len(done) == 1)
        yield from asyncio.wait([self.forward_stdout, self.forward_stderr])
        logging.debug('done stop(%s) -- %d/%d', self.game_dir, self.process.returncode, self.process.pid)

    @asyncio.coroutine
    def stop(self, timeout=2):
        yield from self._stop(timeout)
    
    def cleanup(self):
        self.temp_dir.cleanup()

    def exit_code(self):
        return self.process.returncode
    
    @asyncio.coroutine
    def connect(self, use_ssl=True, use_ipv6=True):
        if use_ssl:
            ssl_context = ssl.create_default_context(cafile=os.path.join(self.game_dir, 'server.pem'))
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE # FIXME: check for exact match to self-signed, or generate dummy CA
        else:
            ssl_context = None
        hostname = '::1' if use_ipv6 else '127.0.0.1'
        port = self.ssl_port if use_ssl else self.normal_port
        return asyncio.open_connection(host=hostname, port=port, ssl=ssl_context)

    def dump_log(self):
        logging.info('dumping log')
        try:
            with open(os.path.join(self.game_dir, 'logs/status'), 'r') as fh:
                status_log = fh.read()
                print("### STATUS LOG ###\n", status_log)
        except:
            pass
        try:
            with open(os.path.join(self.game_dir, 'logs/commands'), 'r') as fh:
                command_log = fh.read()
                print("### COMMAND LOG ###\n", command_log)
        except:
            pass

@asyncio.coroutine
def cancel_after(future, time):
    yield from asyncio.sleep(time)
    future.cancel()

class ReaderWrapper():
    def __init__(self, real_reader, log_func):
        self.real_reader = real_reader
        self.log_func = log_func

    @asyncio.coroutine
    def read(self, n=-1):
        result = yield from self.real_reader.read(n)
        self.log_func(result)
        return result

    @asyncio.coroutine
    def readexactly(self, n):
        result = yield from self.real_reader.readexactly(n)
        self.log_func(result)
        return result

    @asyncio.coroutine
    def readline(self):
        result = yield from self.real_reader.readline()
        self.log_func(result)
        return result

def send_and_quit_wait(reader, writer, main_input):
    writer.write(main_input)
    writer.write(b"\r\npose ENDOFTESTMARKERENDOFTESTMARKER\r\n")
    yield from writer.drain()
    result = b''
    while True:
        line = yield from reader.readline()
        result += line
        if b'ENDOFTESTMARKERENDOFTESTMARKER' in line:
            break
        if len(line) == 0:
            break
    writer.write(b'QUIT\r\n')
    try:
        yield from writer.drain()
    except:
        pass # ignore connection lost, etc.
    result += yield from reader.read()
    writer.close()
    return result

class ServerTestBase(unittest.TestCase):
    use_ssl = None
    use_ipv6 = None
    extra_params = {}
    timezone = 'UTC'

    def setUp(self):
        options = asyncio.get_event_loop().run_until_complete(get_server_options())
        if self.use_ssl and 'SSL' not in options:
            self.skipTest()
        if self.use_ipv6 and 'IPV6' not in options:
            self.skipTest()
        if self.use_ssl == None:
            self.use_ssl = 'SSL' in options
        if self.use_ipv6 == None:
            self.use_ipv6 = 'IPV6' in options
        self.server = Server(params=self.extra_params, timezone=self.timezone)
        self.read_log = b''
        asyncio.get_event_loop().run_until_complete(self.server.start())

    def _log_read(self, s):
        self.read_log += s

    @asyncio.coroutine
    def _connect(self):
       real_reader, writer = yield from self.server.connect(use_ssl=self.use_ssl, use_ipv6=self.use_ipv6)
       reader = ReaderWrapper(real_reader, self._log_read)
       return (reader, writer)
   
    # FIXME: This is probably not actually safe with OpenSSL because we are accessing
    #        the same SSL connection from two threads
    @asyncio.coroutine
    def _co_session_with_input(self, input_func, reader, writer):
        read_result = asyncio.ensure_future(reader.read())
        input_func(writer)
        asyncio.ensure_future(writer.drain())
        result = yield from read_result
        writer.close()
        return result

    @asyncio.coroutine
    def _run_with_reader_writer(self, func):
        reader, writer = yield from self._connect()
        result = yield from func(reader, writer)
        return result

    def _do_full_session_interactive(self, user_func, timeout=10):
        result_future = asyncio.ensure_future(self._run_with_reader_writer(user_func))
        asyncio.ensure_future(cancel_after(result_future, timeout))
        return asyncio.get_event_loop().run_until_complete(result_future)
    
    def _do_full_session_timed_output(self, input_func, timeout=10):
        return self._do_full_session_interactive(lambda reader, writer: self._co_session_with_input(input_func, reader, writer), timeout)

    """
    Run the commands in `input`, then return the result.
    If `autoquit` is True, pose a distinctive pattern, look for it in the output, then QUIT.
    Otherwise, just wait for the server to disconnect.
    """
    def _do_full_session(self, input, timeout=10, add_crlf=True, autoquit=True):
        if add_crlf:
            input = input.replace(b"\n", b"\r\n")
        if autoquit:
            return self._do_full_session_interactive(lambda r, w: send_and_quit_wait(r, w, input), timeout=timeout)
        else:
            return self._do_full_session_timed_output(lambda writer: writer.write(input), timeout=timeout)
    
    """
    Run the commands in `input_setup`; then (unless use_dump is False) shutdown the server and restart it,
    then run the commands in `input_test`. Returns the combined output of both sessions. `prefix` is
    prepending to teach set of commands; this is intended to allow flipping `use_dump` to have two versions
    of tests for things being saved in the database.
    """
    def _do_dump_test(self, input_setup, input_test, prefix=CONNECT_GOD, add_crlf=True, autoquit=True, timeout=5, use_dump=True):
        if use_dump:
            result_one = self._do_full_session(prefix + input_setup + b'\n@shutdown\n', timeout=timeout, autoquit=False,
                add_crlf=add_crlf)
            asyncio.get_event_loop().run_until_complete(self.server.stop())
            self.server.set_output_to_input()
            asyncio.get_event_loop().run_until_complete(self.server.start())
            result_two = self._do_full_session(prefix + input_test, timeout=timeout, autoquit=autoquit)
            return result_one + result_two
        else:
            return self._do_full_session(prefix + input_setup + b'\n' + input_test, 
                autoquit=autoquit, add_crlf=add_crlf, timeout=timeout)

    def _second_user_test(self, main_input, autoquit=True, timeout=5,
                          setup=CONNECT_CREATE_TEST_USER, setup_connect=CONNECT_TEST_USER):
        def _start_session(reader, writer, the_input):
            logging.error('start')
            writer.write(the_input + b"\r\npose ENDOFSETUPMARKERENDOFSETUPMARKER\r\n")
            asyncio.ensure_future(writer.drain())
            while True:
                line = yield from reader.readline()
                logging.error('read <%s>', line)
                if rb'ENDOFSETUPMARKERENDOFSETUPMARKER' in line:
                    break
            return (reader, writer)
        start_future = asyncio.ensure_future(self._run_with_reader_writer(lambda r, w: _start_session(r, w, setup)))
        (one_reader, one_writer) = asyncio.get_event_loop().run_until_complete(start_future)
        user_future = asyncio.ensure_future(self._run_with_reader_writer(lambda r, w: _start_session(r, w, setup_connect)))
        (user_reader, user_writer) = asyncio.get_event_loop().run_until_complete(user_future)
        one_future = asyncio.ensure_future(send_and_quit_wait(one_reader, one_writer, main_input))
        user_future = asyncio.ensure_future(user_reader.read())
        main_result = asyncio.get_event_loop().run_until_complete(one_future)
        user_result = asyncio.get_event_loop().run_until_complete(user_future)
        return (main_result, user_result)

    
    def tearDown(self):
        try:
            asyncio.get_event_loop().run_until_complete(self.server.stop())
        finally:
            self.server.dump_log()
            print("### CONNECTION LOG ###\n", self.read_log.decode(errors='backslashreplace'))
        self.assertEqual(self.server.exit_code(), 0)
        self.server.cleanup()

class MufProgramTestBase(ServerTestBase):
    def _test_program(self, program, before=b"", after=b"", pass_check=True, timeout=10):
        result = self._do_full_session(CONNECT_GOD +
b"""
@program test.muf
i
""" + program + b"""
.
c
q
@set test.muf=D
@act runtest=me
@link runtest=test.muf
""" + before + b"""
runtest
""" + after + b"""
""", timeout=timeout)
        if pass_check:
            self.assertTrue(b'\nTest passed.' in result)
        return result
