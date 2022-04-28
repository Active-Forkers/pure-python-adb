import logging
import re
import time

from ppadb.connection_async import ConnectionAsync


class TransportAsync:
    async def transport(self, connection: ConnectionAsync) -> ConnectionAsync:
        cmd = f"host:transport:{self.serial}"
        await connection.send(cmd)

        return connection

    async def shell(self, cmd: str, timeout=None) -> str:
        conn = await self.create_connection(timeout=timeout)

        cmd = f"shell:{cmd}"
        await conn.send(cmd)

        result = await conn.read_all()
        await conn.close()
        return result.decode('utf-8')

    async def sync(self) -> ConnectionAsync:
        conn = await self.create_connection()

        cmd = "sync:"
        await conn.send(cmd)

        return conn

    async def screencap(self) -> bytes:
        async with await self.create_connection() as conn:
            cmd = "shell:/system/bin/screencap -p"
            await conn.send(cmd)
            result = await conn.read_all()

        if result and len(result) > 5 and result[5] == 0x0d:
            return result.replace(b'\r\n', b'\n')
        else:
            return result
