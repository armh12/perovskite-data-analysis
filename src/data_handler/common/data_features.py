import ast
import pandas as pd
from pymatgen.core.lattice import Lattice
from pymatgen.core.molecular_orbitals import MolecularOrbitals
from pymatgen.core.sites import Site


def filter_valid_perovkiste_by_name(df: pd.DataFrame) -> pd.DataFrame:
    if "name" in df.columns:
        df = df[df["name"].str.endswith("3")]
    return df


def parse_formula(formula: str) -> pd.Series:
    molecular_orbitals = MolecularOrbitals(formula)
    return molecular_orbitals.composition


def decompose_sites(phases_df: pd.DataFrame) -> pd.DataFrame:
    def __parse_site(site_str: str):
        element, coords = site_str.split('@')
        x, y, z = map(float, coords.strip().split())
        sites = Site(element, ((x, y, z)))
        print(sites)
        return element, x, y, z

    def __process_sites(row: pd.Series):
        sites_list = row.sites
        elements = row.__elements
        if isinstance(sites_list, str):
            try:
                sites_list = ast.literal_eval(sites_list)
            except:
                sites_list = []

        site_dict = {}

        for site in sites_list:
            element, x, y, z = __parse_site(site)
            idx = elements.index(element.strip())
            if idx == 0:
                prefix = 'A'
            elif idx == 1:
                prefix = 'B'
            else:
                prefix = "X"
            site_dict[f'{prefix}_x'] = x
            site_dict[f'{prefix}_y'] = y
            site_dict[f'{prefix}_z'] = z

        return pd.Series(site_dict)

    phases_df["__elements"] = phases_df["_composition"].apply(lambda x: list(x.keys()))
    sites_expanded = phases_df[["sites", "__elements"]].apply(__process_sites, axis=1)

    phases_df = pd.concat([phases_df, sites_expanded], axis=1)
    phases_df.drop(columns=["sites", "__elements"], inplace=True)
    return phases_df


def split_element_names(phases_df: pd.DataFrame):
    def __parse_composition(composition_dict: dict):
        element_dict = {}
        for idx, (element_name, element_count) in enumerate(composition_dict.items()):
            if idx == 0:
                prefix = "A"
            elif idx == 1:
                prefix = "B"
            else:
                prefix = "X"
            element_dict[f'{prefix}_element'] = element_name
            element_dict[f'{prefix}_count'] = element_count
        return pd.Series(element_dict)

    parsed = phases_df["_composition"].apply(__parse_composition)
    phases_df = pd.concat([phases_df, parsed], axis=1)
    return phases_df


def parse_unit_cells(phases_df: pd.DataFrame) -> pd.DataFrame:
    def __parse_unit_cell(unit_cell: list[list]) -> pd.Series:
        lattice = Lattice(unit_cell)
        lattice_dict = {
            "a": lattice.a,
            "b": lattice.b,
            "c": lattice.c,
            "alpha": lattice.alpha,
            "beta": lattice.beta,
            "gamma": lattice.gamma,
        }
        return pd.Series(lattice_dict)

    unit_cell_parsed = phases_df["unit_cell"].apply(__parse_unit_cell)
    phases_df = pd.concat([phases_df, unit_cell_parsed], axis=1)
    phases_df.drop(columns=["unit_cell"], inplace=True)
    return phases_df
