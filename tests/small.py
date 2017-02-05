import asyncio
import sys

@asyncio.coroutine
def _do_forward(stream):
    while True:
        data = yield from stream.readline()
        if len(data) == 0:
            break
        sys.stdout.write(data.decode())

@asyncio.coroutine
def foo():
    process = yield from asyncio.create_subprocess_exec('sleep', '1',
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout_future = asyncio.ensure_future(_do_forward(process.stdout))
    stderr_future = asyncio.ensure_future(_do_forward(process.stderr))
    wait_future = asyncio.ensure_future(process.wait())
    done, pending = yield from asyncio.wait([wait_future], timeout=2)
    if len(done) == 0:
        print("None done")
        yield from asyncio.wait([wait_future])
    yield from asyncio.wait([stdout_future, stderr_future])

import logging
logging.basicConfig(level=logging.DEBUG)
asyncio.get_event_loop().run_until_complete(foo())
