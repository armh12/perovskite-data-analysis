import ast
import math
import pandas as pd
from pymatgen.core import Composition
from pymatgen.core.lattice import Lattice
from pymatgen.core.molecular_orbitals import MolecularOrbitals
from pymatgen.core.periodic_table import Element

from data_handler.common.entities import AM3_TO_SM3, AMU_TO_GRAM


def filter_valid_perovkiste_by_name(df: pd.DataFrame, field_name: str) -> pd.DataFrame:
    if field_name in df.columns:
        df = df[df[field_name].str.endswith("3")]
    return df


def parse_formula(formula: str) -> pd.Series:
    molecular_orbitals = MolecularOrbitals(formula)
    return molecular_orbitals.composition


def classify_material(formula: str) -> str:
    """
    Classify a material as 'organic', 'inorganic', or 'semi-organic' based on its formula.

    Heuristics:
      - If the composition contains carbon (C) and hydrogen (H):
           • And if it also contains any metal element (e.g. Pb, Cs, etc.), then it is considered "semi-organic" (a hybrid).
           • If no metal is present, then it is likely "organic".
      - If neither C nor H is present, it is considered "inorganic".

    Note:
      • This is a simple heuristic. For instance, some inorganic compounds like carbonates (containing C) are inorganic,
        and the connectivity in a periodic structure might need more careful treatment.
      • You can refine the list of metals or even check oxidation states for better accuracy.

    Parameters:
      formula (str): The reduced chemical formula (e.g., "CsPbI3", "CH3NH3PbI3", "C10H12N2O").

    Returns:
      str: One of "organic", "semi-organic", or "inorganic".
        """
    comp = Composition(formula)
    elements = [str(el) for el in comp.elements]

    metals = []
    for el in elements:
        try:
            if Element(el).is_metal:
                metals.append(el)
        except Exception:
            pass

    contains_carbon = "C" in elements
    contains_hydrogen = "H" in elements

    if contains_carbon and contains_hydrogen:
        if metals:
            return "semi-organic"
        else:
            return "organic"
    else:
        return "inorganic"


def get_composition_features(df: pd.DataFrame) -> pd.DataFrame:
    def __parse_composition(formula: str) -> pd.Series:
        composition = Composition(formula)
        weight = composition.weight
        avg_elec_negativity = composition.average_electroneg
        scalar_series = pd.Series({
            "weight": weight,
            "avg_elec_negativity": avg_elec_negativity
        })
        return scalar_series

    parsed_df = df["chemical_formula_reduced"].apply(__parse_composition)
    df = pd.concat([df, parsed_df], axis=1)
    return df


def decompose_sites(phases_df: pd.DataFrame) -> pd.DataFrame:
    def __parse_site(site_str: str):
        element, coords = site_str.split('@')
        x, y, z = map(float, coords.strip().split())
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


def parse_lattice_vectors(structures_df: pd.DataFrame) -> pd.DataFrame:
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

    unit_cell_parsed = structures_df["lattice_vectors"].apply(__parse_unit_cell)
    structures_df = pd.concat([structures_df, unit_cell_parsed], axis=1)
    structures_df.drop(columns=["lattice_vectors"], inplace=True)
    return structures_df


def add_density(structures_df: pd.DataFrame) -> pd.DataFrame:
    def _calculate_density(row):
        try:
            lattice = Lattice.from_parameters(
                row['a'], row['b'], row['c'],
                row.get('alpha', 90), row.get('beta', 90), row.get('gamma', 90)
            )
            total_mass = sum(Element(el).atomic_mass for el in row.species_at_sites)
            volume_cm3 = lattice.volume * AM3_TO_SM3
            total_mass_g = total_mass * AMU_TO_GRAM
            density = total_mass_g / volume_cm3
            return density
        except Exception:
            return None

    structures_df['density'] = structures_df.apply(_calculate_density, axis=1)
    return structures_df


def add_tolerance_factor(phases_df: pd.DataFrame) -> pd.DataFrame:
    def _calculate_tolerance(row):
        try:
            r_A = Element(row['A_element']).average_cationic_radius
            r_B = Element(row['B_element']).average_cationic_radius
            r_X = Element(row['X_element']).average_ionic_radius
            if r_A is None or r_B is None or r_X is None:
                return None
            tolerance = (r_A + r_X) / (math.sqrt(2) * (r_B + r_X))
            return tolerance
        except Exception:
            return None

    phases_df['tolerance_factor'] = phases_df.apply(_calculate_tolerance, axis=1)
    return phases_df
