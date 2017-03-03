#!/usr/bin/env python3.6
import asyncio
import logging
import re
import unittest

from fbmuck.server import Server, ServerTestBase

CONNECT = b"connect One potrzebie\n"

class TestEmpty(ServerTestBase):
    def test(self):
        pass

class TestConnectGodSay(ServerTestBase):
    def test(self):
        result = self._do_full_session(CONNECT + 
b"""!say This is a test.
QUIT
""", autoquit=False)
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
            b'You say, "This is a test."' in result
        )
        self.assertTrue(
            b'Come back later!' in result
        )

class TestConnectGodSayV4(TestConnectGodSay):
    use_ipv6 = False

class TestConnectGodSayNoSSL(TestConnectGodSay):
    use_ssl = False

class TestConnectGodSayNoSSLV4(TestConnectGodSay):
    use_ipv6 = False
    use_ssl = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
