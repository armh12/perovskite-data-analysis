import asyncio
from abc import ABC, abstractmethod
from warnings import deprecated

from data_handler.common.base_client import AsyncBaseClient
from data_handler.oqmd.paginator import Paginator


class OQMDAbstractClient(ABC):
    """
    Abstract base class for OQMD clients.
    OQMD API returns test_data by pages - so requests made with paginated params to retrieve all test_data.
    `max_users` param can be set to retrieve only set pages test_data.
    """
    BASE_URL = "https://oqmd.org/oqmdapi"
    OPTIMADE_URL = "https://oqmd.org/optimade"

    def __init__(self,
                 pagination_limit: int = 50,
                 pagination_offset: int = 50):
        self._async_client = AsyncBaseClient(timeout=100, read_timeout=100)
        self._pagination_limit = pagination_limit
        self._pagination_offset = pagination_offset

    @abstractmethod
    async def get_phases(self, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                         max_pages: int | None = None):
        """
        This corresponds to hitting /oqmdapi/formationenergy
        """
        pass

    @abstractmethod
    async def get_structures(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                             max_pages: int | None = None):
        """
        This corresponds to hitting /optimade/structures
        """
        pass

    @abstractmethod
    async def get_entries(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                          max_pages: int | None = None):
        """
        This corresponds to hitting /oqmdapi/entry
        """
        pass

    @abstractmethod
    async def get_calculations(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                               max_pages: int | None = None):
        """
        This corresponds to hitting /oqmdapi/calculation
        """
        pass

    def __get_oqmd_url(self, endpoint: str):
        return f'{self.BASE_URL}/{endpoint}'

    def __get_optimade_url(self, endpoint: str):
        return f'{self.OPTIMADE_URL}/{endpoint}'

    @staticmethod
    def _build_params_for_request(
            fields: list[str] | None = None,
            filters: dict[str, str] | None = None,
    ) -> dict:
        """
        Turn fields, filters, and additional kwargs into query params.
        Be careful with filters, how to set them is shown in docs`
        https://static.oqmd.org/static/docs/restful.html#kw-ref
        """
        params = {}

        if fields:
            params['fields'] = ",".join(fields)
        if filters:
            params['filter'] = " AND ".join([
                f'{key}={value}' for key, value in filters.items()
            ])
        return params

    async def _get_all_data(self, url: str, params: dict, max_pages: int | None = None) -> list:
        response = await self._async_client.get(url, params=params)
        response_json = response.json()
        data_field_name = "test_data" if "calculation" not in url else "results"
        if "meta" not in response_json or "next" not in response_json:
            return response_json[data_field_name]
        meta = response_json.get("meta", None)
        if meta is None and "next" in response_json and not max_pages:
            return response_json[data_field_name]
        data_available = meta.get('data_available', max_pages)
        if not data_available:
            return response_json[data_field_name]
        data_available = max_pages if max_pages is not None else data_available
        paginator = self.__get_paginator(data_available)
        tasks = [
            self._async_client.get(url, params=_params) for _params in paginator.make_params_paginated(params)
        ]

        tasks_results = await asyncio.gather(*tasks)
        tasks_results.append(response_json)
        results = []
        for task_result in tasks_results:
            if isinstance(task_result, dict):
                results.extend(task_result[data_field_name])
            else:
                results.extend(task_result.json()[data_field_name])
        return results

    def __get_paginator(self, max_pages: int) -> Paginator:
        return Paginator(pagination_offset=self._pagination_offset,
                         pagination_limit=self._pagination_limit,
                         total_pages_count=max_pages)

    async def _oqmd_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                            max_pages: int | None = None):
        url = self.__get_oqmd_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return await self._get_all_data(url=url,
                                        params=params,
                                        max_pages=max_pages)

    async def _optimade_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                                max_pages: int | None = None):
        url = self.__get_optimade_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return await self._get_all_data(url=url,
                                        params=params,
                                        max_pages=max_pages)


class OQMDAsyncClient(OQMDAbstractClient):
    """
    Asynchronous OQMD data_handler that implements the abstract endpoints.
    """

    def __init__(self):
        super().__init__()

    async def get_phases(self, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                         max_pages: int | None = None) -> list[dict]:
        return await self._oqmd_request("formationenergy",
                                        fields=fields,
                                        filters=filters,
                                        max_pages=max_pages)

    async def get_structures(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                             max_pages: int | None = None) -> list[dict]:
        return await self._optimade_request("structures",
                                            fields=fields,
                                            filters=filters,
                                            max_pages=max_pages)

    @deprecated("Endpoint does not working in API")
    async def get_entries(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                          max_pages: int | None = None) -> list[dict]:
        return await self._oqmd_request("entry",
                                        fields=fields,
                                        filters=filters,
                                        max_pages=max_pages)

    async def get_calculations(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                               max_pages: int | None = None) -> list[dict]:
        return await self._oqmd_request("calculation",
                                        fields=fields,
                                        filters=filters,
                                        max_pages=max_pages)
