import pandas as pd

from data_handler.common.data_features import decompose_sites, split_element_names, filter_valid_perovkiste_by_name, \
    parse_formula, parse_unit_cells
from data_handler.oqmd.client import OQMDAsyncClient


class PerovskiteDataHandler:
    PEROVSKITE_FILTER = {"generic": "ABC3"}
    phases_fields = ["name", "entry_id", "formationenergy_id", "spacegroup", "volume", "ntypes", "natoms", "band_gap",
                     "delta_e", "stability", "unit_cell", "sites"]

    def __init__(self,
                 client: OQMDAsyncClient, ):
        self.client = client

    async def get_phases(self, max_pages: int | None = None) -> pd.DataFrame:
        json_response = await self.client.get_phases(self.phases_fields, self.PEROVSKITE_FILTER, max_pages)
        df = pd.DataFrame(json_response)
        df = filter_valid_perovkiste_by_name(df)
        df["_composition"] = df["name"].apply(parse_formula)
        df = decompose_sites(df)
        df = split_element_names(df)
        df = parse_unit_cells(df)
        df.drop(columns=["_composition"], inplace=True)
        df.rename(columns={"delta_e": "e_hull", "entry_id": "id"})
        return df

    async def get_structures(self, offset: int | None = None, max_pages: int | None = None) -> pd.DataFrame:
        json_response = await self.client.get_structures(self.PEROVSKITE_FILTER, max_pages)
        attrs = [_json_response["attributes"] for _json_response in json_response]
        df = pd.DataFrame(attrs)
        return df

    async def get_calculations(self, offset: int | None = None, max_pages: int | None = None) -> pd.DataFrame:
        json_response = await self.client.get_calculations(None, self.PEROVSKITE_FILTER, max_pages)
        df = pd.DataFrame(json_response)
        return df
