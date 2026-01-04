from backend.app.models import ProxyPeer
from backend.app.core.config import settings
from backend.app.services.vpn.wg_ssh import WireGuardSSHClient
from backend.app.utils.wireguard import generate_keypair


class WireGuardService:

    @staticmethod
    def _get_ssh():
        return WireGuardSSHClient(
            host=settings.WG_HOST,
            user=settings.WG_SSH_USER,
            key_path=settings.WG_SSH_KEY_PATH,
        )

    @staticmethod
    def create_peer(db, user, device):
        private_key, public_key = generate_keypair()
        ip = allocate_ip(db)

        config = f"""[Interface]
PrivateKey = {private_key}
Address = {ip}/32

[Peer]
PublicKey = {settings.WG_SERVER_PUBLIC_KEY}
Endpoint = {settings.WG_SERVER_ENDPOINT}
AllowedIPs = {settings.WG_SERVER_ALLOWED_IPS}
PersistentKeepalive = 25
"""

        peer = ProxyPeer(
            user_id=user.id,
            device_id=device.id,
            protocol="wireguard",
            config=config,
            public_key=public_key,
            allowed_ips=f"{ip}/32",
            is_active=True,
        )

        db.add(peer)
        db.commit()
        db.refresh(peer)

        # 🔐 добавляем peer на сервер
        ssh = WireGuardService._get_ssh()
        ssh.add_peer(public_key, peer.allowed_ips)

        return peer

    @staticmethod
    def _allocate_ip(db) -> str:
        used_ips = set()

        peers = db.query(ProxyPeer).filter(
            ProxyPeer.protocol == "wireguard"
        ).all()

        for peer in peers:
            for line in peer.config.splitlines():
                if line.startswith("Address"):
                    used_ips.add(line.split("=")[1].strip().split("/")[0])

        for i in range(2, 255):
            ip = f"10.10.0.{i}"
            if ip not in used_ips:
                return ip

        raise RuntimeError("No free WireGuard IPs")
    
    @staticmethod
    def delete_peer_completely(peer, db):
        ssh = WireGuardService._get_ssh()

        ssh.remove_peer(peer.public_key)

        db.delete(peer)
        db.commit()

    @staticmethod
    def disable_peer(peer, db):
        if not peer.is_active:
            return

        ssh = WireGuardService._get_ssh()
        ssh.remove_peer(peer.public_key)

        peer.is_active = False
        db.commit()

    @staticmethod
    def enable_peer(peer, db):
        if peer.is_active:
            return

        ssh = WireGuardService._get_ssh()
        ssh.add_peer(peer.public_key, peer.allowed_ips)

        peer.is_active = True
        db.commit()
