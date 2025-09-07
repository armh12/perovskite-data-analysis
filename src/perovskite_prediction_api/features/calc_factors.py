import numpy as np


def compute_tolerance_factor(r_A_eff: float, r_B: float, r_C_eff: float) -> float:
    """
    Compute the tolerance factor for the perovskite.
    Returns:
        float: Tolerance factor.
    """
    if r_B + r_C_eff == 0:
        return float('inf')
    return (r_A_eff + r_C_eff) / (np.sqrt(2) * (r_B + r_C_eff))


def compute_octahedral_factor(r_B: float, r_C_eff: float) -> float:
    """
    Compute the octahedral factor for the perovskite.
    Args:
        r_B (float): B-site radius.
        r_X_eff (float): Effective X-site radius.
    Returns:
        float: Octahedral factor.
    """
    if r_C_eff == 0:
        return float('inf')
    return r_B / r_C_eff
