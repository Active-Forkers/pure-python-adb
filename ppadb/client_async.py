from ppadb.command.host_async import HostAsync
from ppadb.connection_async import ConnectionAsync
from ppadb.device import Device


class ClientAsync(HostAsync):
    def __init__(self, host='127.0.0.1', port=5037) -> None:
        self.host = host
        self.port = port

    async def create_connection(self, timeout=None) -> ConnectionAsync:
        conn = ConnectionAsync(self.host, self.port, timeout)
        return await conn.connect()

    async def device(self, serial: str) -> Device:
        devices = await self.devices()

        for device in devices:
            if device.serial == serial:
                return device

        return None
