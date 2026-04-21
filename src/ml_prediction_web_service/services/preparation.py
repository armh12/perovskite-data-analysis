from typing import Any, Dict, List

import pandas as pd
import numpy as np

from ml_prediction_web_service.entities.dictionary import (
    Site, Dimension, SpaceGroup, ETLStack, HTLStack, BackContact, CellArchitecture, StabilityProtocol
)
from ml_prediction_web_service.entities.entities import (
    PerovskiteComposition,
    PCET80PredictionRequest,
    BandGapPredictionRequest,
    JVDefaultPCEPredictionRequest
)
from ml_prediction_web_service.services.features.calc_factors import compute_octahedral_factor, compute_tolerance_factor
from ml_prediction_web_service.services.features.structure_features import (
    calculate_effective_radii,
    calculate_weighted_properties,
    compute_dimensionality_indicator,
    compute_space_group
)

# EXACT Feature Lists from training script to ensure correct ordering for CatBoost
MATERIAL_PHYS = ['r_A', 'en_A', 'mass_A', 'r_C', 'en_C', 'mass_C', 'tolerance_factor', 'octahedral_factor', 'radius_ratio_ab', 'en_diff_bc', 'mass_ratio_ab']
COEF_FEATURES = ['A_1_coef', 'A_2_coef', 'A_3_coef', 'B_1_coef', 'C_1_coef', 'C_2_coef']
CAT_SITES = ['A_1', 'A_2', 'A_3', 'B_1', 'C_1', 'C_2']
CAT_DEVICE = ['dimension', 'cell_architecture', 'etl_stack_sequence', 'htl_stack_sequence', 'backcontact_stack_sequence', 'stability_protocol']
PROCESSING_PHYS = ['perovskite_annealing_temp', 'perovskite_annealing_time']
STRESS_PHYS = ['acc_temp', 'acc_humidity', 'stability_light_intensity']
JV_FEATURES = ['jv_default_pce', 'jv_default_voc', 'jv_default_jsc', 'jv_default_ff']

def _normalize_enum_value(val: Any, enum_cls: Any) -> str:
    if val is None:
        return ""
    if hasattr(val, 'nm'):
        return val.nm
    try:
        member = enum_cls(val)
        if member:
            return member.nm
    except:
        pass
    return str(val)

def clean_categorical_data(df: pd.DataFrame, cat_cols: List[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna('None').astype(str)
    return df

def enforce_feature_order(df: pd.DataFrame, feature_list: List[str], cat_cols: List[str]) -> pd.DataFrame:
    """Ensures DataFrame has correct columns, correct order, and categorical columns are strings."""
    # Ensure all columns exist (fill with None/0 if missing)
    for col in feature_list:
        if col not in df.columns:
            df[col] = None
    
    # Select and order
    df = df[feature_list]
    
    # Clean Categorical
    df = clean_categorical_data(df, cat_cols)
    return df

def _create_features_dict(composition_entity: PerovskiteComposition, is_inorganic: bool) -> Dict[str, Any]:
    features = {
        "A_1": None, "A_2": None, "A_3": None,
        "A_1_coef": 0.0, "A_2_coef": 0.0, "A_3_coef": 0.0,
        "B_1": None, 
        "B_1_coef": 0.0,
        "C_1": None, "C_2": None, "C_3": None,
        "C_1_coef": 0.0, "C_2_coef": 0.0, "C_3_coef": 0.0,
        "composition_inorganic": is_inorganic
    }

    def __fill_site(site_list, prefix, max_count):
        for i, element_fraction in enumerate(site_list[:max_count], start=1):
            features[f"{prefix}_{i}"] = element_fraction.name.nm
            features[f"{prefix}_{i}_coef"] = element_fraction.frequence

    __fill_site(composition_entity.A_site, Site.A.value, 3)
    __fill_site(composition_entity.B_site, Site.B.value, 1)
    __fill_site(composition_entity.C_site, Site.C.value, 3)

    r_A = calculate_effective_radii(composition_entity.A_site)
    r_B = calculate_effective_radii(composition_entity.B_site)
    r_C = calculate_effective_radii(composition_entity.C_site)
    
    en_A, mass_A = calculate_weighted_properties(composition_entity.A_site)
    en_B, mass_B = calculate_weighted_properties(composition_entity.B_site)
    en_C, mass_C = calculate_weighted_properties(composition_entity.C_site)

    features.update({
        "r_A": r_A, "r_B": r_B, "r_C": r_C,
        "en_A": en_A, "en_B": en_B, "en_C": en_C,
        "mass_A": mass_A, "mass_B": mass_B, "mass_C": mass_C,
    })
    
    tf = compute_tolerance_factor(r_A, r_B, r_C)
    of = compute_octahedral_factor(r_B, r_C)
    features["octahedral_factor"] = of
    features["tolerance_factor"] = tf
    
    features["radius_ratio_ab"] = r_A / r_B if r_B else 0
    features["en_diff_bc"] = abs(en_B - en_C) if en_B is not None and en_C is not None else 0
    features["mass_ratio_ab"] = mass_A / mass_B if mass_B else 0

    is_2d = compute_dimensionality_indicator(r_A)
    features["is_2d"] = is_2d
    features["dimension"] = Dimension.TWO_DIM.nm if is_2d == 1 else Dimension.THREE_DIM.nm

    return features

def prepare_perovskites_composition_input(request: BandGapPredictionRequest) -> pd.DataFrame:
    features = _create_features_dict(request.perovskite_composition, request.inorganic_composition)
    df = pd.DataFrame([features])
    
    # Feature list from train_models_optuna: material_phys + coef_features + cat_sites + ['dimension']
    bg_feature_list = MATERIAL_PHYS + COEF_FEATURES + CAT_SITES + ['dimension']
    cat_cols = CAT_SITES + ['dimension']
    
    return enforce_feature_order(df, bg_feature_list, cat_cols)

def prepare_ts80_prediction_df(request: PCET80PredictionRequest) -> pd.DataFrame:
    features = _create_features_dict(request.perovskite_composition, request.inorganic_composition)
    
    # Device/Stress Params
    features.update({
        "cell_architecture": _normalize_enum_value(request.cell_architecture, CellArchitecture),
        "etl_stack_sequence": _normalize_enum_value(request.etl_stack_sequence, ETLStack),
        "htl_stack_sequence": _normalize_enum_value(request.htl_stack_sequence, HTLStack),
        "backcontact_stack_sequence": _normalize_enum_value(request.backcontact, BackContact),
        "stability_protocol": _normalize_enum_value(request.stability_protocol, StabilityProtocol),
        "stability_light_intensity": request.stability_light_intensity,
        "acc_temp": request.acc_temp,
        "acc_humidity": request.acc_humidity,
        "perovskite_annealing_temp": request.perovskite_annealing_temp,
        "perovskite_annealing_time": request.perovskite_annealing_time,
        "jv_default_pce": request.pce_initial,
        "jv_default_voc": request.voc_initial,
        "jv_default_jsc": request.jsc_initial,
        "jv_default_ff": request.ff_initial,
        "band_gap": request.band_gap,
        "stress_proxy": request.pce_initial * features["tolerance_factor"]
    })
    
    df = pd.DataFrame([features])
    
    # Feature list from train_models_optuna: 
    # material_phys + coef_features + processing_phys + stress_phys + jv_features + ['band_gap', 'stress_proxy'] + all_cat
    all_cat = list(set(CAT_SITES + CAT_DEVICE))
    t80_feature_list = MATERIAL_PHYS + COEF_FEATURES + PROCESSING_PHYS + STRESS_PHYS + JV_FEATURES + ['band_gap', 'stress_proxy'] + all_cat
    
    return enforce_feature_order(df, t80_feature_list, all_cat)

def prepare_jv_pce_prediction_df(request: JVDefaultPCEPredictionRequest) -> pd.DataFrame:
    features = _create_features_dict(request.perovskite_composition, request.inorganic_composition)
    
    features.update({
        "cell_architecture": _normalize_enum_value(request.cell_architecture, CellArchitecture),
        "etl_stack_sequence": _normalize_enum_value(request.etl_stack_sequence, ETLStack),
        "htl_stack_sequence": _normalize_enum_value(request.htl_stack_sequence, HTLStack),
        "backcontact_stack_sequence": _normalize_enum_value(request.backcontact, BackContact),
        "perovskite_annealing_temp": request.perovskite_annealing_temp,
        "perovskite_annealing_time": request.perovskite_annealing_time,
        "band_gap": request.band_gap
    })
    
    df = pd.DataFrame([features])
    
    # Feature list from train_models_optuna: material_phys + coef_features + processing_phys + ['band_gap'] + all_cat
    all_cat = list(set(CAT_SITES + CAT_DEVICE))
    pce_feature_list = MATERIAL_PHYS + COEF_FEATURES + PROCESSING_PHYS + ['band_gap'] + all_cat
    
    return enforce_feature_order(df, pce_feature_list, all_cat)
