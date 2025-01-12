import pytest
import os
import pandas as pd

from data_handler.oqmd.client import OQMDAsyncClient

TEST_DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "test_data"))


@pytest.fixture(name="oqmd_client")
def oqmd_client_fixture() -> OQMDAsyncClient:
    return OQMDAsyncClient()


@pytest.fixture(name="df_phases")
def df_phases_fixture() -> pd.DataFrame:
    df = pd.read_parquet(os.path.join(TEST_DATA_PATH, "df_phases.parquet"))
    return df


@pytest.fixture(name="df_calcs_fixture")
def df_calcs_fixture() -> pd.DataFrame:
    df = pd.read_parquet(os.path.join(TEST_DATA_PATH, "df_calcs.parquet"))
    return df


@pytest.fixture(name="df_structures")
def df_structures_fixture() -> pd.DataFrame:
    df = pd.read_parquet(os.path.join(TEST_DATA_PATH, "df_structures.parquet"))
    return df
