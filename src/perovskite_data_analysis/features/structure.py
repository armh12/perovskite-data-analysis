from typing import Dict, Tuple

import numpy as np

from perovskite_data_analysis.entities.elements import Elements
from perovskite_data_analysis.entities.structure import SpaceGroup


def compute_effective_radii(composition: Dict[str, Dict[str, float]]) -> Tuple[float, float, float] | None:
    """
    Compute the effective ionic radii for A-site, B-site, and C-site.
    Returns:
        Tuple[float, float, float]: (r_A_eff, r_B, r_C_eff)
    """
    try:
        r_A_eff = 0.0
        r_C_eff = 0.0
        for elem_name, coeff in composition['A'].items():
            element = Elements.get_element_by_name(elem_name)
            r_A_eff += coeff * element.ionic_radii
        for elem_name, coeff in composition['C'].items():
            element = Elements.get_element_by_name(elem_name)
            r_C_eff += (coeff / 3.0) * element.ionic_radii  # Normalize by total C-site stoichiometry (3)
        r_B = sum(
            coeff * Elements.get_element_by_name(elem_name).ionic_radii for elem_name, coeff in
            composition['B'].items())
        return r_A_eff, r_B, r_C_eff
    except ValueError:
        return None


def compute_dimensionality_indicator(r_A_eff: float) -> int:
    """
    Compute the dimensionality indicator (1 for 2D if r_A_eff > 3.0, 0 for 3D).
    Returns:
        int: Dimensionality indicator (1 or 0).
    """
    return 1 if r_A_eff > 3.0 else 0


def predict_space_group(tolerance_factor: float, is_2d: int) -> str:
    """
    Predict the space group of a perovskite based on tolerance factor and dimensionality.
    Args:
        tolerance_factor (float): Tolerance factor (t).
        is_2d (float): Is perovskite 2D
    Returns:
        str: Predicted space group.
    """
    if is_2d:
        return SpaceGroup.RUDDLESDEN_POPEN.value
    else:
        if tolerance_factor > 0.9:
            return SpaceGroup.CUBIC.value
        elif 0.8 < tolerance_factor <= 0.9:
            return SpaceGroup.TETRAGONAL.value
        else:
            return SpaceGroup.ORTHOROMBIC.value


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
