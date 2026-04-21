from typing import Tuple, List

import pandas as pd

from ml_prediction_web_service.entities.dictionary import SpaceGroup, Dimension
from ml_prediction_web_service.entities.entities import ElementFraction


def calculate_effective_radii(fractions: List[ElementFraction]) -> float:
    r_eff = 0.0
    total_coef = 0.0
    for item in fractions:
        r_eff += item.frequence * item.name.ionic_radii
        total_coef += item.frequence
    return r_eff / total_coef if total_coef > 0 else 0.0


def calculate_weighted_properties(fractions: List[ElementFraction]) -> Tuple[float, float]:
    """
    Calculate weighted average electronegativity and atomic mass.
    Returns:
        Tuple[float, float]: (weighted_en, weighted_mass)
    """
    weighted_en = 0.0
    weighted_mass = 0.0
    total_coef = 0.0
    for item in fractions:
        weighted_en += item.frequence * item.name.electronegativity
        weighted_mass += item.frequence * item.name.atomic_mass
        total_coef += item.frequence
    if total_coef == 0:
        return 0.0, 0.0
    return weighted_en / total_coef, weighted_mass / total_coef


def compute_dimensionality_indicator(r_a_eff: float) -> int:
    """
    Compute the dimensionality indicator (1 for 2D if r_A_eff > 3.0, 0 for 3D).
    Returns:
        int: Dimensionality indicator (1 or 0).
    """
    return 1 if r_a_eff > 3.0 else 0


def compute_ionic_radius_ratios(r_A_eff: float, r_B: float, r_C_eff: float) -> Tuple[float, float]:
    """
    Compute additional ionic radius ratios.

    Args:
        r_A_eff (float): Effective A-site radius.
        r_B (float): B-site radius.
        r_C_eff (float): Effective C-site radius.

    Returns:
        Tuple[float, float]: (r_A_eff/r_C_eff, r_B/r_A_eff)
    """
    r_A_to_C = r_A_eff / r_C_eff if r_C_eff != 0 else float('inf')
    r_B_to_A = r_B / r_A_eff if r_A_eff != 0 else float('inf')
    return r_A_to_C, r_B_to_A


def compute_space_group(tolerance_factor: float, dimension: float, is_inorganic: bool) -> str | None:
    if pd.isna(tolerance_factor):
        return pd.NA

    # 3D Perovskites
    if dimension == Dimension.THREE_DIM.nm:
        if 0.9 <= tolerance_factor <= 1.0:
            return SpaceGroup.CUBIC.nm  # Cubic
        elif 0.8 <= tolerance_factor < 0.9:
            return SpaceGroup.ORTHOROMBIC.nm if is_inorganic else SpaceGroup.TETRAGONAL.nm  # Orthorhombic or tetragonal
        elif tolerance_factor < 0.8:
            return SpaceGroup.ORTHOROMBIC.nm  # Orthorhombic
        else:  # t > 1.0
            return SpaceGroup.HEXAGONAL.nm  # Hexagonal

    # 2D Perovskites
    elif dimension == Dimension.TWO_DIM.nm:
        return SpaceGroup.RUDDLESDEN_POPEN.nm  # Layered structure

    # 2D3D Mixture
    elif dimension == Dimension.TWO_THREE_DIM_MIXTURE.nm:
        return SpaceGroup.RUDDLESDEN_POPEN.nm if tolerance_factor < 0.9 else SpaceGroup.ORTHOROMBIC.nm
    # 0D Perovskites
    elif dimension == Dimension.ZERO_DIM.nm:
        return 'Unknown'  # Often molecular, not well-defined
