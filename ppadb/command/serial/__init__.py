from ppadb.command import Command


class Serial(Command):
    def _execute_cmd(self, cmd: str, with_response=True) -> str:
        conn = self.create_connection(set_transport=False)

        with conn:
            conn.send(cmd)
            if with_response:
                result = conn.receive()
                return result
            else:
                conn.check_status()

    def forward(self, local: str, remote: str, norebind=False) -> None:
        if norebind:
            cmd = f"host-serial:{self.serial}:forward:norebind:{local};{remote}"
        else:
            cmd = f"host-serial:{self.serial}:forward:{local};{remote}"

        self._execute_cmd(cmd, with_response=False)

    def list_forward(self) -> dict:
        # According to https://android.googlesource.com/platform/system/core/+/master/adb/adb_listeners.cpp#129
        # And https://android.googlesource.com/platform/system/core/+/master/adb/SERVICES.TXT#130
        # The 'list-forward' always lists all existing forward connections from the adb server
        # So we need filter these by self.
        cmd = f"host-serial:{self.serial}:list-forward"
        result = self._execute_cmd(cmd)

        forward_map = {}

        for line in result.split('\n'):
            if line:
                serial, local, remote = line.split()
                if serial == self.serial:
                    forward_map[local] = remote

        return forward_map

    def killforward(self, local: str) -> None:
        cmd = f"host-serial:{self.serial}:killforward:{local}"
        self._execute_cmd(cmd, with_response=False)

    def killforward_all(self) -> None:
        # killforward-all command ignores the <host-prefix> and remove all the forward mapping.
        # So we need to implement this function by self
        forward_map = self.list_forward()
        for local, remote in forward_map.items():
            self.killforward(local)

    def get_device_path(self) -> str:
        cmd = f"host-serial:{self.serial}:get-devpath"
        return self._execute_cmd(cmd)

    def get_serial_no(self) -> str:
        cmd = f"host-serial:{self.serial}:get-serialno"
        return self._execute_cmd(cmd)

    def get_state(self) -> str:
        cmd = f"host-serial:{self.serial}:get-state"
        return self._execute_cmd(cmd)
