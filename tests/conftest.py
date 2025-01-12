import pytest

from client.oqmd.client import OQMDAsyncClient


@pytest.fixture(name="oqmd_client")
def oqmd_client_fixture() -> OQMDAsyncClient:
    return OQMDAsyncClient()
