from abc import ABC, abstractmethod
import httpx

class BaseClient(ABC):
    @abstractmethod
    def get(self, url: str, params: dict | None, headers: dict | None = None) -> httpx.Response:
        pass

    @abstractmethod
    def post(self, url: str, request_body_json: dict | None, headers: dict | None = None) -> httpx.Response:
        pass


class AsyncBaseClient(BaseClient):
    """
    Base client for interacting with httpx client.
    """
    def __init__(self,
                 timeout: int,
                 connect_timeout: int | None = None,
                 read_timeout: int | None = None,
                 write_timeout: int | None = None,):
        self.timeout = httpx.Timeout(timeout=timeout,
                                     read=read_timeout,
                                     write=write_timeout,
                                     connect=connect_timeout,
                                     )
        self.__async_client = httpx.AsyncClient(timeout=timeout)


    async def get(self, url: str, params: dict | None, headers: dict | None = None) -> httpx.Response:
        response = await self.__async_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    async def post(self, url: str, request_body_json: dict | None, headers: dict | None = None) -> httpx.Response:
        response = await self.__async_client.post(url, headers=headers, json=request_body_json)
        response.raise_for_status()
        return response
