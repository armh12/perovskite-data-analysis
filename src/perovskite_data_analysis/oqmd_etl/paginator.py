import math
from dataclasses import dataclass


class Paginator:
    """
    Class for paginating the requests for OQMD API.
    """
    @dataclass
    class OQMDPage:
        offset: int
        limit: int

    def __init__(self,
                 pagination_offset: int,
                 pagination_limit: int,
                 total_pages_count: int) -> None:
        self.pagination_offset = pagination_offset
        self.pagination_limit = pagination_limit
        self.total_pages_count = total_pages_count
        self.pages: list[Paginator.OQMDPage] = self.__make_pagination()

    def __make_pagination(self):
        total_pages = math.ceil(self.total_pages_count / self.pagination_limit)
        pages = []
        cur_pagination_offset = self.pagination_offset
        for _ in range(total_pages):
            page = Paginator.OQMDPage(offset=cur_pagination_offset + self.pagination_limit, limit=self.pagination_limit)
            pages.append(page)
            cur_pagination_offset = page.offset
        return pages

    def make_params_paginated(self, params: dict) -> list[dict]:
        paginated_params = []
        for page in self.pages:
            cur_params = params.copy()
            cur_params.update({"offset": page.offset, "limit": page.limit})
            paginated_params.append(cur_params)
        return paginated_params
