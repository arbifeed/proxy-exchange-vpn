from abc import ABC, abstractmethod
from backend.app.models import User, Device


class BaseVPNService(ABC):

    @abstractmethod
    def generate_config(self, user: User, device: Device) -> dict:
        pass

    @abstractmethod
    def revoke_device(self, device: Device) -> None:
        pass

    @abstractmethod
    def add_peer(self, peer_data: dict):
        pass

    @abstractmethod
    def remove_peer(self, peer_data: dict):
        pass
