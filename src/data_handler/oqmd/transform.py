import pandas as pd

from data_handler.oqmd.client import OQMDAsyncClient


async def get_phases(client: OQMDAsyncClient, fields: list[str] | None = None, filters: dict[str, str] | None = None,
                     max_pages: int | None = None) -> pd.DataFrame:
    json_response = await client.get_phases(fields, filters, max_pages)
    df = pd.DataFrame(json_response)
    return df

async def get_structures(client: OQMDAsyncClient, fields: list[str] = None, filters: dict[str, str] | None = None,
                         max_pages: int | None = None) -> pd.DataFrame:
    json_response = await client.get_structures(fields, filters, max_pages)
    attrs = [_json_response["attributes"] for _json_response in json_response]
    print(attrs)
    df = pd.DataFrame(attrs)
    return df

async def get_calculations(client: OQMDAsyncClient, fields: list[str] = None, filters: dict[str, str] | None = None,
                           max_pages: int | None = None) -> pd.DataFrame:
    json_response = await client.get_calculations(fields, filters, max_pages)
    df = pd.DataFrame(json_response)
    return df

import asyncio
df = asyncio.run(get_calculations(OQMDAsyncClient(), max_pages=50, filters={"generic": "ABC3"}))
df.to_csv("df_calcs.csv")

