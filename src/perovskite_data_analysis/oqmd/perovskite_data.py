import pandas as pd

from perovskite_data_analysis.common.data_features import decompose_sites, split_element_names, \
    filter_valid_perovkiste_by_name, \
    parse_formula, parse_lattice_vectors, add_density, add_tolerance_factor, get_composition_features, classify_material
from perovskite_data_analysis.oqmd.client import OQMDClient


class PerovskiteDataHandler:
    PEROVSKITE_FILTER = {"generic": "ABC3"}
    phases_fields = ["name", "entry_id", "spacegroup", "volume", "ntypes", "natoms", "band_gap",
                     "delta_e", "stability", "sites"]
    structures_fields = ["chemical_formula_reduced", "_oqmd_entry_id", "lattice_vectors", "species_at_sites"]

    def __init__(self,
                 client: OQMDClient, ):
        self.client = client

    def get_phases(self, max_pages: int = 50) -> pd.DataFrame:
        json_response = self.client.get_phases(self.phases_fields, self.PEROVSKITE_FILTER, max_pages)
        df = pd.DataFrame(json_response)
        df = filter_valid_perovkiste_by_name(df, "name")
        df["_composition"] = df["name"].apply(parse_formula)
        df = decompose_sites(df)
        df = split_element_names(df)
        df = add_tolerance_factor(df)
        df["classification"] = df["name"].apply(classify_material)
        df.drop(columns=["_composition"], inplace=True)
        df.rename(columns={"delta_e": "e_hull", "entry_id": "id"}, inplace=True)
        return df

    def get_structures(self, max_pages: int = 50) -> pd.DataFrame:
        json_response = self.client.get_structures(self.PEROVSKITE_FILTER, max_pages)
        attrs = [_json_response["attributes"] for _json_response in json_response]
        df = pd.DataFrame(attrs)
        df = df[self.structures_fields]
        df = filter_valid_perovkiste_by_name(df, "chemical_formula_reduced")
        df["_composition"] = df["chemical_formula_reduced"].apply(parse_formula)
        df = parse_lattice_vectors(df)
        df = add_density(df)
        df = get_composition_features(df)
        df.rename(columns={"_oqmd_entry_id": "id"}, inplace=True)
        df.drop(columns=["_composition", "species_at_sites"], inplace=True)
        return df

    def get_calculations(self, max_pages: int = 50) -> pd.DataFrame:
        json_response = self.client.get_calculations(None, self.PEROVSKITE_FILTER, max_pages)
        df = pd.DataFrame(json_response)
        return df
