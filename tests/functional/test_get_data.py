import pytest
import pandas as pd

import data_handler.oqmd.transform as transform

MAX_PAGES = 100

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


@pytest.mark.asyncio
async def test_get_phases_returns_valid_data(oqmd_client):
    df = await transform.get_phases(oqmd_client, max_pages=MAX_PAGES)
    assert df is not None
    assert not df.empty
    print("\n", df)

