from .adapter import ProviderAdapter


class MockProvider(ProviderAdapter):

    def get_proxy(self, api_key: str):
        return {
            "ip": "123.45.67.89",
            "port": 8080,
            "protocol": "http",
            "user": api_key,
            "password": "test",
        }
