import os
import pandas as pd
from logging import getLogger

from data_handler.oqmd.client import OQMDClient
from data_handler.oqmd.perovskite_data import PerovskiteDataHandler


class PerovskiteLoader:
    DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))

    def __init__(self, handler: PerovskiteDataHandler, offset: int = 50):
        self.data_handler = handler
        self.log = getLogger(__name__)
        self.offset = offset

    def run(self):
        self.process_phases()
        self.process_structures()

    def process_phases(self):
        self.log.info("Started phases df extraction")
        path = f'{self.DIR_PATH}/phases.parquet'
        phases_df_total = pd.DataFrame()
        offset = self.offset
        while phases_df_total.empty:
            phases_df_total = self.data_handler.get_phases(request_offset=offset, request_limit=offset + 50)
            self.log.info(f"Finished phases df extraction for offset - {offset}")
            self.save(phases_df_total, path)
            offset += self.offset
        self.log.info("Finished phases df processing")

    def process_structures(self):
        self.log.info("Started structures df extraction")
        path = f'{self.DIR_PATH}/structures.parquet'
        phases_df_total = pd.DataFrame()
        offset = self.offset
        while phases_df_total.empty:
            phases_df_total = self.data_handler.get_structures(request_offset=offset, request_limit=offset + 50)
            self.log.info(f"Finished structures df extraction for offset - {offset}")
            self.save(phases_df_total, path)
            offset += self.offset
        self.log.info("Finished structures df processing")

    @staticmethod
    def save(df: pd.DataFrame, path_to_save: str):
        dir_name = os.path.dirname(path_to_save)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        if os.path.exists(path_to_save):
            df_base = pd.read_parquet(path_to_save)
            df = pd.concat([df, df_base])
            df.drop_duplicates(subset=["id"], inplace=True)
        df.to_parquet(path_to_save, index=False)


if __name__ == '__main__':
    client = OQMDClient()
    handler = PerovskiteDataHandler(client)
    loader = PerovskiteLoader(handler)
    loader.run()
