import pandas as pd

from data_handler.common.data_features import decompose_sites, split_element_names, filter_perovkiste_by_name, \
    parse_formula
from data_handler.oqmd.client import OQMDAsyncClient

PEROVSKITE_FILTER = {"generic": "ABC3"}

async def get_phases(client: OQMDAsyncClient, fields: list[str] | None = None,
                     max_pages: int | None = None) -> pd.DataFrame:
    if fields is not None and "name" not in fields:
        raise ValueError("Name field is mandatory")
    json_response = await client.get_phases(fields, PEROVSKITE_FILTER, max_pages)
    df = pd.DataFrame(json_response)
    composition_df = pd.json_normalize(df["name"].apply(parse_formula))
    print(composition_df.head())
    df = pd.concat([df, composition_df], axis=1)
    df = decompose_sites(df)
    print(df)
    # df = split_element_names(df)
    return df


async def get_structures(client: OQMDAsyncClient, fields: list[str] = None, filters: dict[str, str] | None = None,
                         max_pages: int | None = None) -> pd.DataFrame:
    json_response = await client.get_structures(fields, filters, max_pages)
    attrs = [_json_response["attributes"] for _json_response in json_response]
    df = pd.DataFrame(attrs)
    return df


async def get_calculations(client: OQMDAsyncClient, fields: list[str] = None, filters: dict[str, str] | None = None,
                           max_pages: int | None = None) -> pd.DataFrame:
    json_response = await client.get_calculations(fields, filters, max_pages)
    df = pd.DataFrame(json_response)
    return df
