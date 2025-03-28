from typing import Dict

from perovskite_data_analysis.entities.elements import Elements


def compute_charge_balance(composition: Dict[str, Dict[str, float]]) -> float:
    """
    Compute the charge balance (q_A_eff + q_B + 3*q_C_eff).
    Returns:
        float: Charge balance.
    """
    q_A_eff = 0.0
    q_C_eff = 0.0
    for elem_name, coeff in composition['A'].items():
        element = Elements.get_element_by_name(elem_name)
        q_A_eff += coeff * element.charge
    for elem_name, coeff in composition['C'].items():
        element = Elements.get_element_by_name(elem_name)
        q_C_eff += (coeff / 3.0) * element.charge
    q_B = sum(coeff * Elements.get_element_by_name(elem_name).charge for elem_name, coeff in composition['B'].items())
    return q_A_eff + q_B + 3 * q_C_eff

