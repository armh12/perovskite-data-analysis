import logging
from abc import ABC, abstractmethod
from functools import wraps
import httpx
import time

from perovskite_data_analysis.common.base_client import Client
from perovskite_data_analysis.oqmd.paginator import Paginator

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

    def __init__(self,
                 logger: logging.Logger,):
        self._client = Client(timeout=100, read_timeout=100)
        self.log = logger

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
    def _get_all_data(self, url: str, params: dict, data_field_name: str, max_pages: int = 50) -> list:
        """
        OQMD API have next URL in response body, but requesting to next is returning 301 status code response,
        so we will use paginator to avoiding next URL usage.
        """
        # make single request to get all metadata
        first_response = self._client.get(url, params=params)
        first_response_json = first_response.json()
        # make paginator
        metadata = first_response_json["meta"]
        data_available = metadata["data_available"]
        offset = metadata["data_returned"]
        paginator = self.__get_paginator(offset, max_pages, data_available)
        # add first_response to results
        responses = []
        responses = self._register_result(responses, first_response_json[data_field_name])

        # make paginated requests
        for _param in paginator.make_params_paginated(params):
            self.log.info(f'Make request on offset - {_param["offset"]}')
            response = self._client.get(url, params=_param)
            responses = self._register_result(responses, response.json()[data_field_name])
        return responses


    def _oqmd_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                      max_pages: int = 50):
        url = self.__get_oqmd_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return self._get_all_data(url=url,
                                  params=params,
                                  data_field_name="data" if "calculation" not in url else "results",
                                  max_pages=max_pages)

    def _optimade_request(self, endpoint: str, fields: list[str] = None, filters: dict[str, str] | None = None,
                          max_pages: int = 50):
        url = self.__get_optimade_url(endpoint)
        params = self._build_params_for_request(fields=fields, filters=filters)
        return self._get_all_data(url=url,
                                  params=params,
                                  max_pages=max_pages,
                                  data_field_name="data")

    @staticmethod
    def __get_paginator(pagination_offset: int, pagination_limit: int, max_pages: int) -> Paginator:
        return Paginator(pagination_offset=pagination_offset,
                         pagination_limit=pagination_limit,
                         total_pages_count=max_pages)

    @staticmethod
    def _register_result(responses: list, response: list | dict):
        if isinstance(response, list):
            responses.extend(response)
        elif isinstance(response, dict):
            responses.append(response)
        return responses


class OQMDClient(OQMDAbstractClient):
    """
    Asynchronous OQMD perovskite_data_analysis that implements the abstract endpoints.
    """

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)

    def get_phases(self, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                   max_pages: int = 50) -> list[dict]:
        self.log.info("Start phases extraction")
        return self._oqmd_request("formationenergy",
                                  fields=fields,
                                  filters=filters,
                                  max_pages=max_pages,)

    def get_structures(self, filters: dict[str, str] | None = None, max_pages: int = 50) -> list[dict]:
        self.log.info("Start structures extraction")
        return self._optimade_request("structures",
                                      filters=filters,
                                      max_pages=max_pages,)

    def get_calculations(self, fields: list[str] = None, filters: dict[str, str] | None = None,
                         max_pages: int = 50) -> list[dict]:
        self.log.info("Start calculations extraction")
        return self._oqmd_request("calculation",
                                  fields=fields,
                                  filters=filters,
                                  max_pages=max_pages,)
