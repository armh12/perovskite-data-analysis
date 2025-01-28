from data_handler.oqmd.client import OQMDAsyncClient
from data_handler.oqmd.perovskite_data import PerovskiteDataHandler


class PerovskiteLoader:
    def __init__(self, oqmd_client: OQMDAsyncClient, data_handler: PerovskiteDataHandler):
        self.oqmd_client = oqmd_client
        self.data_handler = data_handler

    async def process_phases(self):
        ...

