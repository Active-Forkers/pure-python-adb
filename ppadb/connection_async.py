import asyncio
import struct
import socket

from ppadb.protocol import Protocol
from ppadb.utils.logger import AdbLogging

logger = AdbLogging.get_logger(__name__)


class ConnectionAsync:
    def __init__(self, host='localhost', port=5037, timeout=None) -> None:
        self.host = host
        self.port = int(port)
        self.timeout = timeout

        self.reader = None
        self.writer = None

    async def __aenter__(self) -> ConnectionAsync:
        return self

    async def __aexit__(self, type, value, traceback) -> None:
        await self.close()

    async def connect(self) -> ConnectionAsync:
        logger.debug("Connect to ADB server - %s:%d", self.host, self.port)

        try:
            if self.timeout:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), self.timeout)
            else:
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        except (OSError, asyncio.TimeoutError) as e:
            raise RuntimeError(f"ERROR: connecting to {self.host}:{self.port} {e}.\nIs adb running on your computer?")

        # Really?
        return self

    async def close(self) -> None:
        logger.debug("Connection closed...")
        
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except OSError:
                pass

        self.reader = None
        self.writer = None

    ##############################################################################################################
    #
    # Send command & Receive command result
    #
    ##############################################################################################################
    async def _recv(self, length: int) -> bytes:
        return await asyncio.wait_for(self.reader.read(length), self.timeout)

    async def _send(self, data: bytes) -> None:
        # Guessing the return type
        # https://github.com/python/cpython/blob/e25799d27d049237849c471b25db3b128b1bfa08/Lib/asyncio/streams.py#L325
        # As the transport can be anything from user there is no definition of the write method in the source code of asyncio
        self.writer.write(data)
        await asyncio.wait_for(self.writer.drain(), self.timeout)

    async def receive(self) -> str:
        nob = int((await self._recv(4)).decode('utf-8'), 16)
        return (await self._recv(nob)).decode('utf-8')

    async def send(self, msg: str) -> bool:
        msg = Protocol.encode_data(msg)
        logger.debug(msg)
        await self._send(msg)
        return await self._check_status()

    async def _check_status(self) -> bool:
        recv = (await self._recv(4)).decode('utf-8')
        if recv != Protocol.OKAY:
            error = (await self._recv(1024)).decode('utf-8')
            raise RuntimeError(f"ERROR: {repr(recv)} {error}")

        return True

    ##############################################################################################################
    #
    # Socket read/write
    #
    ##############################################################################################################
    async def read_all(self) -> bytearray:
        data = bytearray()

        while True:
            recv = await self._recv(4096)
            if not recv:
                break
            data += recv

        return data

    async def read(self, length=0) -> bytes:
        data = await self._recv(length)
        return data

    async def write(self, data: bytes) -> None:
        await self._send(data)
