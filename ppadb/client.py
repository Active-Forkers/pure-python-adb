from ppadb.command.host import Host
from ppadb.connection import Connection
from ppadb.device import Device
from ppadb.utils.logger import AdbLogging

logger = AdbLogging.get_logger(__name__)

class Client(Host):
    def __init__(self, host='127.0.0.1', port=5037) -> None:
        self.host = host
        self.port = port

    def create_connection(self, timeout=None) -> Connection:
        # never used and should instead be a static method
        conn = Connection(self.host, self.port, timeout)
        conn.connect()
        return conn

    def device(self, serial: str) -> Device:
        devices = self.devices()

        for device in devices:
            if device.serial == serial:
                return device

        return None
