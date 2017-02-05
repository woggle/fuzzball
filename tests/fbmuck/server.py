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
                 game_dir=None):
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

    @asyncio.coroutine
    def start(self):
        logging.error('start(%s)', self.game_dir)
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
        self.process = \
            yield from asyncio.create_subprocess_exec(*command_line, cwd=self.game_dir,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        self.forward_stdout = asyncio.ensure_future(self._forward_stdout())
        self.forward_stderr = asyncio.ensure_future(self._forward_stderr())
        self.process_wait = asyncio.ensure_future(self.process.wait())
        yield from asyncio.sleep(1) # wait for server to bind, etc.

    def _stop(self, timeout):
        logging.error('about to SIGTERM to %d', self.process.pid)
        self.process.send_signal(signal.SIGTERM)
        logging.error('about to start wait')
        wait_future = self.process_wait
        done, pending = yield from asyncio.wait([wait_future], timeout=timeout)
        logging.error('tried waiting')
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
        logging.error('here')
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

class ServerTestBase(unittest.TestCase):
    use_ssl = None
    use_ipv6 = None
    extra_params = {}

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
        self.server = Server(params=self.extra_params)
        asyncio.get_event_loop().run_until_complete(self.server.start())

    @asyncio.coroutine
    def _connect(self):
        return (yield from self.server.connect(use_ssl=self.use_ssl, use_ipv6=self.use_ipv6))
   
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
        result = yield from asyncio.ensure_future(func(reader, writer))
        return result

    def _do_full_session_interactive(self, user_func, timeout=10):
        future = asyncio.ensure_future(self._run_with_reader_writer(user_func))
        asyncio.ensure_future(cancel_after(future, timeout))
        return asyncio.get_event_loop().run_until_complete(future)
    
    def _do_full_session_timed_output(self, input_func, timeout=10):
        return self._do_full_session_interactive(lambda reader, writer: self._co_session_with_input(input_func, reader, writer), timeout)

    def _do_full_session(self, input, timeout=10, add_crlf=True):
        if add_crlf:
            input = input.replace(b"\n", b"\r\n")
        return self._do_full_session_timed_output(lambda writer: writer.write(input), timeout=timeout)

    def tearDown(self):
        try:
            asyncio.get_event_loop().run_until_complete(self.server.stop())
        finally:
            self.server.dump_log()
        self.assertEqual(self.server.exit_code(), 0)
        self.server.cleanup()
