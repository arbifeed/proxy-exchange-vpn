import paramiko


class WireGuardSSHClient:
    def __init__(self, host: str, user: str, key_path: str):
        self.host = host
        self.user = user
        self.key_path = key_path

    def _exec(self, command: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self.host,
            username=self.user,
            key_filename=self.key_path,
            timeout=10,
        )
        stdin, stdout, stderr = ssh.exec_command(command)
        err = stderr.read().decode()
        if err:
            raise RuntimeError(err)
        return stdout.read().decode()

    def add_peer(self, public_key: str, allowed_ips: str):
        self._exec(
            f"wg set wg0 peer {public_key} allowed-ips {allowed_ips}"
        )
        self._exec("wg-quick save wg0")

    def remove_peer(self, public_key: str):
        self._exec(f"wg set wg0 peer {public_key} remove")
        self._exec("wg-quick save wg0")


# ✅ ВАЖНО: создаём ОДИН экземпляр
wg_ssh = WireGuardSSHClient(
    host="85.192.26.92",
    user="root",
    key_path="/root/.ssh/id_rsa",
)
