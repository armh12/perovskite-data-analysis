from abc import ABC, abstractmethod
from warnings import deprecated
from functools import wraps
import httpx
import time

from data_handler.common.base_client import Client
from data_handler.oqmd.paginator import Paginator

RETRY_DELAY_SEC = 15
RETRY_COUNT = 10


def http_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(RETRY_COUNT):
            try:
                return func(*args, **kwargs)
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code in (500, 502, 503):
                    print(f"Server side issue, retry in {RETRY_DELAY_SEC} seconds")
                    time.sleep(RETRY_DELAY_SEC)
                    continue
                elif status_code in (403, 404, 406):
                    print(f"Client side error - {exc.response.text}")
                    raise exc

    return wrapper


class OQMDAbstractClient(ABC):
    """
    Abstract base class for OQMD clients.
    OQMD API returns test_data by pages - so requests made with paginated params to retrieve all test_data.
    `max_users` param can be set to retrieve only set pages test_data.
    """
    BASE_URL = "https://oqmd.org/oqmdapi"
    OPTIMADE_URL = "https://oqmd.org/optimade"

    def __init__(self, ):
        self._client = Client(timeout=100, read_timeout=100)

    @abstractmethod
    def get_phases(self, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                   max_pages: int | None = None):
        """
        This corresponds to hitting /oqmdapi/formationenergy
        """
        pass

    @abstractmethod
    def get_structures(self, filters: dict[str, str] | None = None, max_pages: int | None = None):
        """
        This corresponds to hitting /optimade/structures
        """
        pass

    @abstractmethod
    def get_entries(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                    max_pages: int | None = None):
        """
        This corresponds to hitting /oqmdapi/entry
        """
        pass

    @abstractmethod
    def get_calculations(self, fields: list[str] = None, filters: dict[str, str] | None = None,
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

    @http_error_handler
    def _get_all_data(self, url: str, params: dict, max_pages: int | None = None,
                      request_offset: int = 50, request_limit: int | None = None) -> list:
        response = self._client.get(url, params=params)
        response_json = response.json()
        data_field_name = "data" if "calculation" not in url else "results"
        if "meta" not in response_json and "next" not in response_json:
            return response_json[data_field_name]
        meta = response_json.get("meta", None)
        if meta is None and "next" in response_json and not max_pages:
            return response_json[data_field_name]
        data_available = request_limit if request_limit is not None else meta.get('data_available', max_pages)
        if not data_available:
            return response_json[data_field_name]
        data_available = max_pages if max_pages is not None else data_available
        paginator = self.__get_paginator(data_available, request_offset, request_limit)
        responses = [response_json[data_field_name], ]
        for _params in paginator.make_params_paginated(params):
            _response = self._client.get(url, params=_params)
            _response_json = response.json()
            if isinstance(_response_json, dict):
                responses.append(_response_json[data_field_name])
            else:
                responses.extend(_response_json[data_field_name])
        return responses

    def _oqmd_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                      max_pages: int | None = None, request_offset: int = 50, request_limit: int | None = None):
        url = self.__get_oqmd_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return self._get_all_data(url=url,
                                  params=params,
                                  max_pages=max_pages,
                                  request_offset=request_offset,
                                  request_limit=request_limit)

    def _optimade_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                          max_pages: int | None = None, request_offset: int = 50, request_limit: int | None = None):
        url = self.__get_optimade_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return self._get_all_data(url=url,
                                  params=params,
                                  max_pages=max_pages,
                                  request_offset=request_offset,
                                  request_limit=request_limit)

    @staticmethod
    def __get_paginator(pagination_offset: int, pagination_limit: int, max_pages: int) -> Paginator:
        return Paginator(pagination_offset=pagination_offset,
                         pagination_limit=pagination_limit,
                         total_pages_count=max_pages)


class OQMDClient(OQMDAbstractClient):
    """
    Asynchronous OQMD data_handler that implements the abstract endpoints.
    """

    def __init__(self):
        super().__init__()

    def get_phases(self, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                   max_pages: int | None = None, request_offset: int = 50, request_limit: int | None = None) -> list[
        dict]:
        return self._oqmd_request("formationenergy",
                                  fields=fields,
                                  filters=filters,
                                  max_pages=max_pages,
                                  request_offset=request_offset,
                                  request_limit=request_limit)

    def get_structures(self, filters: dict[str, str] | None = None, max_pages: int | None = None,
                       request_offset: int = 50, request_limit: int | None = None) -> list[dict]:
        return self._optimade_request("structures",
                                      filters=filters,
                                      max_pages=max_pages,
                                      request_offset=request_offset,
                                      request_limit=request_limit
                                      )

    @deprecated("Endpoint does not working in API")
    def get_entries(self, fields: list[str] = None, filters: dict[str, str] | None = None, max_pages: int | None = None,
                    request_offset: int = 50, request_limit: int | None = None) -> list[dict]:
        return self._oqmd_request("entry",
                                  fields=fields,
                                  filters=filters,
                                  max_pages=max_pages,
                                  request_offset=request_offset,
                                  request_limit=request_limit)

    def get_calculations(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                         max_pages: int | None = None, request_offset: int = 50, request_limit: int | None = None) \
            -> list[dict]:
        return self._oqmd_request("calculation",
                                  fields=fields,
                                  filters=filters,
                                  max_pages=max_pages,
                                  request_offset=request_offset,
                                  request_limit=request_limit)
