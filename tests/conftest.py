import pytest
import os
import pandas as pd
from google.oauth2.credentials import Credentials

from perovskite_data_analysis.common.credentials import google_credentials
from perovskite_data_analysis.common.storage import GoogleDriveStorage
from perovskite_data_analysis.oqmd_etl.client import OQMDClient
from perovskite_data_analysis.oqmd_etl.configuration import build_configuration
from perovskite_data_analysis.oqmd_etl.perovskite_data import PerovskiteDataHandler

TEST_DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "test_data"))

config = build_configuration()


@pytest.fixture(name="oqmd_client")
def oqmd_client_fixture() -> OQMDClient:
    return OQMDClient(logger=config.logger)


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


@pytest.fixture(name="perovskite_provider")
def perovskite_provider_fixture(oqmd_client):
    return PerovskiteDataHandler(oqmd_client)


@pytest.fixture(name="credentials")
def credentials_fixture() -> Credentials:
    return google_credentials()


@pytest.fixture(name="google_storage")
def google_storage_fixture(credentials):
    return GoogleDriveStorage(credentials)
