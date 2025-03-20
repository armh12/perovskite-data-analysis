"""
Cause we have data from various sources - need to make one standard for data and process it.
"""
from enum import Enum


class ColumnNames(Enum):
    FORMULA = "formula"
    # energies
    BAND_GAP = "e_band_gap"
    FERMI_LEVEL = "e_fermi_level"
    E_HULL = "e_hull"
    TOLERANCE_FACTOR = "tolerance_factor"
    # atomic properties
    ATOMIC_MASS = "atomic_mass"
    VOLUME = "volume"
    DENSITY = "density"
    # electro properties
    ENERGY_ADDED_ELECTRO = "e_add_electrons"
    ENERGY_REQUIRED_ELECTRO = "e_request_electrons"
    # sizes
    VDW_RADIUS_MEAN = "vdw_radius_mean"
    CATIONIC_RADIUS_MEAN = "cationic_radius_mean"
    ANIONIC_RADIUS_MEAN = "anionic_radius_mean"
    # THERMO
    BP_MEAN = "bp_mean"
    MP_MEAN = "mp_mean"
    HEAT_FUS_MEAN = "heat_fus_mean"
    HEAT_VAP_MEAN = "heat_vap_mean"
    E_HEAT_MEAN = "e_heat_mean"
    HEAT_CONDUCTION_NUM = "k_heat"
    # magnetism
    POLARIZATION_MEAN = "polarization_mean"
    MAGNETIC_MOMENT_MEAN = "magnetic_moment_mean"
