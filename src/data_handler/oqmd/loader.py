import os
import pandas as pd
from logging import getLogger

from data_handler.oqmd.client import OQMDClient
from data_handler.oqmd.perovskite_data import PerovskiteDataHandler


class PerovskiteLoader:
    DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))

    def __init__(self, handler: PerovskiteDataHandler):
        self.data_handler = handler
        self.log = getLogger(__name__)

    def run(self):
        self.process_phases()
        self.process_structures()

    def process_phases(self):
        self.log.info("Started phases df extraction")
        phases_df_total = self.data_handler.get_phases()
        self.log.info("Finished phases df extraction")
        path = f'{self.DIR_PATH}/phases.parquet'
        self.save(phases_df_total, path)
        self.log.info("Finished phases df processing")

    def process_structures(self):
        self.log.info("Started structures df extraction")
        structures_df_total = self.data_handler.get_structures()
        self.log.info("Finished structures df extraction")
        path = f'{self.DIR_PATH}/structures.parquet'
        self.save(structures_df_total, path)
        self.log.info("Finished structures df processing")

    @staticmethod
    def save(df: pd.DataFrame, path_to_save: str):
        dir_name = os.path.dirname(path_to_save)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        df.to_parquet(path_to_save, index=False)


if __name__ == '__main__':
    client = OQMDClient()
    handler = PerovskiteDataHandler(client)
    loader = PerovskiteLoader(handler)
    loader.run()
