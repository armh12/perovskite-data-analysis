import os
import pandas as pd

from perovskite_data_analysis.oqmd.configuration import Configuration, build_configuration
from perovskite_data_analysis.oqmd.enrich import process_enrich_phases, process_enrich_structures


class PerovskiteLoader:
    DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))

    def __init__(self, configuration: Configuration):
        self.data_handler = configuration.handler
        self.log = configuration.logger

    def run(self):
        self.process_phases()
        self.process_structures()
        process_enrich_phases()
        process_enrich_structures()

    def process_phases(self):
        filepath = f'{self.DIR_PATH}/phases.parquet'
        data = self.data_handler.get_phases()
        self.save(data, filepath)

    def process_structures(self):
        filepath = f'{self.DIR_PATH}/structures.parquet'
        data = self.data_handler.get_structures()
        self.save(data, filepath)

    def merge_loaded_data(self):
        phases_path = f'{self.DIR_PATH}/phases.parquet'
        if not os.path.exists(phases_path):
            raise ValueError("No phases file found")
        structures_path = f'{self.DIR_PATH}/structures.parquet'
        if not os.path.exists(structures_path):
            raise ValueError("No structures file found")
        phases_df = pd.read_parquet(phases_path)
        structures_df = pd.read_parquet(structures_path)
        perovskites_df = pd.merge(phases_df, structures_df, left_on="id", right_on="id")
        total_path = f'{self.DIR_PATH}/perovskites.parquet'
        self.save(perovskites_df, total_path)

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
    config = build_configuration()
    loader = PerovskiteLoader(config)
    loader.run()
