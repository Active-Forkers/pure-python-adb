from ppadb.command.host import Host
from ppadb.connection import Connection
from ppadb.utils.logger import AdbLogging

logger = AdbLogging.get_logger(__name__)

class Client(Host):
    def __init__(self, host='127.0.0.1': str, port=5037: int) -> None:
        self.host = host
        self.port = port

    def create_connection(self, timeout=None: float) -> Connection:
        # never used and should instead be a static method
        conn = Connection(self.host, self.port, timeout)
        conn.connect()
        return conn

    def device(self, serial: str):
        devices = self.devices()

        for device in devices:
            if device.serial == serial:
                return device

        return None
