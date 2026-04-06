import httpx

class ApiClient:
    def __init__(self, base_url: str, timeout: float=20.0) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def  __aenter__(self) -> "ApiClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client is not None:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.client.get(url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.client.post(url, **kwargs)