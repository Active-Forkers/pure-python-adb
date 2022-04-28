try:
    from asyncio import get_running_loop
except ImportError:  # pragma: no cover
    from asyncio import get_event_loop as get_running_loop  # Python 3.6 compatibility

import re
import os

from ppadb.command.transport_async import TransportAsync
from ppadb.connection_async import ConnectionAsync
from ppadb.client_async import ClientAsync as Client
from ppadb.sync_async import SyncAsync


def _get_src_info(src: str) -> tuple:
    exists = os.path.exists(src)
    isfile = os.path.isfile(src)
    isdir = os.path.isdir(src)
    basename = os.path.basename(src)
    walk = None if not isdir else list(os.walk(src))

    return exists, isfile, isdir, basename, walk


class DeviceAsync(TransportAsync):
    INSTALL_RESULT_PATTERN = "(Success|Failure|Error)\s?(.*)"
    UNINSTALL_RESULT_PATTERN = "(Success|Failure.*|.*Unknown package:.*)"

    def __init__(self, client: ClientAsync, serial: str) -> None:
        self.client = client
        self.serial = serial

    async def create_connection(self, set_transport=True, timeout=None) -> ConnectionAsync:
        conn = await self.client.create_connection(timeout=timeout)

        if set_transport:
            await self.transport(conn)

        return conn

    async def _push(self, src: str, dest: str, mode: int, progress) -> None:
        # Like the sync one, cannot guess the type of progress
        # Create a new connection for file transfer
        sync_conn = await self.sync()
        sync = SyncAsync(sync_conn)

        async with sync_conn:
            await sync.push(src, dest, mode, progress)

    async def push(self, src: str, dest: str, mode=0o644, progress=None) -> None:
        exists, isfile, isdir, basename, walk = await get_running_loop().run_in_executor(None, _get_src_info, src)
        if not exists:
            raise FileNotFoundError(f"Cannot find {src}")

        if isfile:
            await self._push(src, dest, mode, progress)

        elif isdir:
            for root, dirs, files in walk:
                root_dir_path = os.path.join(basename, root.replace(src, ""))

                await self.shell(f"mkdir -p {dest}/{root_dir_path}")

                for item in files:
                    await self._push(os.path.join(root, item), os.path.join(dest, root_dir_path, item), mode, progress)

    async def pull(self, src: str, dest: str) -> bytearray:
        sync_conn = await self.sync()
        sync = SyncAsync(sync_conn)

        async with sync_conn:
            return await sync.pull(src, dest)
