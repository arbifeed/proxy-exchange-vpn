class ProviderAdapter:
    """Базовый интерфейс поставщика прокси/VLESS"""

    def get_proxy(self, api_key: str):
        raise NotImplementedError
