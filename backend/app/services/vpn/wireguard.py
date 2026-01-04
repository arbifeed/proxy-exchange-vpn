import subprocess

from backend.app.services.vpn.base import BaseVPNService
from backend.app.services.vpn.wg_ssh import WireGuardSSHClient
from backend.app.models import Device


class WireGuardService(BaseVPNService):

    SERVER_PUBLIC_KEY = "fyu+wAa7Mv9IWzPQraveaQTUUIKb8Za5ZZK91VWKbSQ="
    SERVER_ENDPOINT = "85.192.26.92:51820"
    SERVER_ALLOWED_IPS = "0.0.0.0/0"

    WG_INTERFACE = "wg0"

    def __init__(self):
        self.ssh = WireGuardSSHClient(
            host="85.192.26.92",
            user="root",
            key_path="/path/to/id_rsa",
        )

    # ---------- KEY GENERATION ----------

    @staticmethod
    def generate_keypair() -> tuple[str, str]:
        private_key = subprocess.check_output(["wg", "genkey"]).strip()
        public_key = subprocess.check_output(
            ["wg", "pubkey"], input=private_key
        ).strip()

        return private_key.decode(), public_key.decode()

    # ---------- PEER LOGIC ----------

    def generate_peer_config(self, device: Device) -> dict:
        private_key, public_key = self.generate_keypair()
        client_ip = f"10.10.0.{device.id + 1}/32"

        config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 8.8.8.8

[Peer]
PublicKey = {self.SERVER_PUBLIC_KEY}
Endpoint = {self.SERVER_ENDPOINT}
AllowedIPs = {self.SERVER_ALLOWED_IPS}
PersistentKeepalive = 25
"""

        return {
            "private_key": private_key,
            "public_key": public_key,
            "address": client_ip,
            "config": config.strip(),
        }

    def add_peer(self, peer_data: dict) -> None:
        self.ssh.add_peer(
            public_key=peer_data["public_key"],
            allowed_ips=peer_data["address"],
        )

    def remove_peer(self, public_key: str) -> None:
        self.ssh.remove_peer(public_key)
