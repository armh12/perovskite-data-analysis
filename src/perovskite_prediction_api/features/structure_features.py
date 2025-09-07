from typing import Dict, Tuple

import numpy as np
import pandas as pd

from perovskite_prediction_api.entities.v1.elements import Elements
from perovskite_prediction_api.entities.v1.structure import SpaceGroup, Dimensions, Sites


def compute_effective_radii(composition: Dict[str, Dict[str, float]]) -> Tuple[float, float, float] | None:
    """
    Compute the effective ionic radii for A-site, B-site, and C-site.
    Returns:
        Tuple[float, float, float]: (r_A_eff, r_B, r_C_eff)
    """
    try:
        r_A_eff = 0.0
        r_C_eff = 0.0
        for elem_name, coeff in composition[Sites.A.value].items():
            element = Elements.get_element_by_name(elem_name)
            r_A_eff += coeff * element.ionic_radii
        for elem_name, coeff in composition[Sites.C.value].items():
            element = Elements.get_element_by_name(elem_name)
            r_C_eff += (coeff / 3.0) * element.ionic_radii  # Normalize by total C-site stoichiometry (3)
        r_B = sum(
            coeff * Elements.get_element_by_name(elem_name).ionic_radii for elem_name, coeff in
            composition['B'].items())
        return r_A_eff, r_B, r_C_eff
    except ValueError as exc:
        raise exc


def compute_dimensionality_indicator(r_A_eff: float) -> int:
    """
    Compute the dimensionality indicator (1 for 2D if r_A_eff > 3.0, 0 for 3D).
    Returns:
        int: Dimensionality indicator (1 or 0).
    """
    return 1 if r_A_eff > 3.0 else 0


def get_space_group(tolerance_factor: float, is_2d: int) -> str:
    """
    Predict the space group of a perovskite based on tolerance factor and dimensionality.
    Args:
        tolerance_factor (float): Tolerance factor (t).
        is_2d (float): Is perovskite 2D
    Returns:
        str: Predicted space group.
    """
    if is_2d:
        return SpaceGroup.RUDDLESDEN_POPEN.value[0]
    else:
        if tolerance_factor > 0.9:
            return SpaceGroup.CUBIC.value[0]
        elif 0.8 < tolerance_factor <= 0.9:
            return SpaceGroup.TETRAGONAL.value[0]
        else:
            return SpaceGroup.ORTHOROMBIC.value[0]


def compute_ionic_radius_ratios(r_A_eff: float, r_B: float, r_X_eff: float) -> Tuple[float, float]:
    """
    Compute additional ionic radius ratios.

    Args:
        r_A_eff (float): Effective A-site radius.
        r_B (float): B-site radius.
        r_X_eff (float): Effective X-site radius.

    Returns:
        Tuple[float, float]: (r_A_eff/r_X_eff, r_B/r_A_eff)
    """
    r_A_to_X = r_A_eff / r_X_eff if r_X_eff != 0 else float('inf')
    r_B_to_A = r_B / r_A_eff if r_A_eff != 0 else float('inf')
    return r_A_to_X, r_B_to_A


def compute_centrosymmetry_indicator(space_group: str) -> int:
    """
    Compute a binary indicator for whether the space group is centrosymmetric.
    Args:
        space_group (str): Space group symbol.
    Returns:
        int: 1 if centrosymmetric, 0 if non-centrosymmetric.
    """
    return 1 if space_group in SpaceGroup._member_names_ else 0


def compute_hydrophobicity_indicator(composition: Dict[str, Dict[str, float]]) -> int:
    """
    Compute the hydrophobicity indicator (1 if any A-site ion is hydrophobic, 0 otherwise).
    Returns:
        int: Hydrophobicity indicator (1 or 0).
    """
    is_hydrophobic = any(Elements.get_element_by_name(elem_name).hydrophobicity for elem_name in composition['A'])
    return 1 if is_hydrophobic else 0


def compute_effective_polarizability(composition: Dict[str, Dict[str, float]], site: str) -> float:
    """
    Compute the effective polarizability for a given site (A, B, or X).
    Args:
        composition (Dict[str, Dict[str, float]]): Perovskite composition.
        site (str): Site to compute polarizability for ('A', 'B', or 'X').
    Returns:
        float: Effective polarizability.
    """
    polarizability = 0.0
    for elem_name, coeff in composition[site].items():
        element = Elements.get_element_by_name(elem_name)
        r = element.ionic_radii
        m = element.atomic_mass
        weight = coeff if site in ['A', 'B'] else coeff / 3.0
        polarizability += weight * (r ** 3 / m if m != 0 else 0)
    return polarizability


def compute_shannon_entropy(composition: Dict[str, Dict[str, float]], site: str) -> float:
    """
    Compute the Shannon entropy of the composition for a given site.
    Args:
        composition (Dict[str, Dict[str, float]]): Perovskite composition.
        site (str): Site to compute entropy for ('A' or 'X').
    Returns:
        float: Shannon entropy.
    """
    entropy = 0.0
    for elem_name, coeff in composition[site].items():
        x_i = coeff if site == 'A' else coeff / 3.0
        if x_i > 0:
            entropy -= x_i * np.log(x_i)
    return entropy


def compute_space_group(tolerance_factor: float, dimension: float, is_inorganic: bool) -> str | pd.NA:
    if pd.isna(tolerance_factor):
        return pd.NA

    # 3D Perovskites
    if dimension == Dimensions.THREE_DIM.value:
        if 0.9 <= tolerance_factor <= 1.0:
            return SpaceGroup.CUBIC.value  # Cubic
        elif 0.8 <= tolerance_factor < 0.9:
            return SpaceGroup.ORTHOROMBIC.value if is_inorganic else SpaceGroup.TETRAGONAL.value  # Orthorhombic or tetragonal
        elif tolerance_factor < 0.8:
            return SpaceGroup.ORTHOROMBIC.value  # Orthorhombic
        else:  # t > 1.0
            return SpaceGroup.HEXAGONAL.value  # Hexagonal

    # 2D Perovskites
    elif dimension == Dimensions.TWO_DIM.value:
        return SpaceGroup.RUDDLESDEN_POPEN.value  # Layered structure

    # 2D3D Mixture
    elif dimension == Dimensions.TWO_THREE_DIM_MIXTURE.value:
        return SpaceGroup.RUDDLESDEN_POPEN.value if tolerance_factor < 0.9 else SpaceGroup.ORTHOROMBIC.value
    # 0D Perovskites
    elif dimension == Dimensions.ZERO_DIM.value:
        return 'Unknown'  # Often molecular, not well-defined


def create_composition_dict(row: pd.Series) -> dict[str, dict[str, float]]:
    """
    Used for easy access for feature calc in dataframe.Service and helper function.
    """
    composition = {Sites.A.value: {}, Sites.B.value: {}, Sites.C.value: {}}

    expected_totals = {Sites.A.value: 1.0, Sites.B.value: 1.0, Sites.C.value: 3.0}
    max_slots = {Sites.A.value: 5, Sites.B.value: 3, Sites.C.value: 4}

    for ion_prefix in [Sites.A.value, Sites.B.value, Sites.C.value]:
        site_dict = {}
        for num in range(1, max_slots[ion_prefix] + 1):
            elem_key = f"{ion_prefix}_{num}"
            coef_key = f"{ion_prefix}_{num}_coef"

            if elem_key not in row:
                continue

            elem = row[elem_key]
            coef = row[coef_key] if coef_key in row else -1

            if elem == -1 or elem == "-1":
                continue
            if isinstance(elem, str) and ("|" in elem or elem.strip() == ""):
                continue

            if isinstance(elem, str):
                elem = elem.replace('(', '').replace(')', '').strip()

            site_dict[elem] = coef
        try:
            site_dict = {k: float(v) for k, v in site_dict.items() if v != 0}
        except ValueError:
            return pd.NA

        if not site_dict:
            return pd.NA

        if any(coef == -1 for coef in site_dict.values()):
            num_ions = len(site_dict)
            inferred_coef = expected_totals[ion_prefix] / num_ions
            site_dict = {ion: inferred_coef for ion in site_dict}
        else:
            total_coef = sum(site_dict.values())
            if total_coef > 0:
                scaling_factor = expected_totals[ion_prefix] / total_coef
                site_dict = {ion: coef * scaling_factor for ion, coef in site_dict.items()}
        composition[ion_prefix] = site_dict

    return composition
