import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from typing import List, Dict, Any

from ml_prediction_web_service.components import AppComponents
from ml_prediction_web_service.entities.dictionary import (
    Element
)
from ml_prediction_web_service.entities.entities import (
    BandGapDiscoveryRequest,
    BandGapDiscoveryResponse,
    SolarPanelDiscoveryRequest,
    SolarPanelDiscoveryResponse,
    ElementFraction,
    PerovskiteComposition
)
from ml_prediction_web_service.services.preparation import (
    MATERIAL_PHYS, COEF_FEATURES, CAT_SITES, CAT_DEVICE, PROCESSING_PHYS, STRESS_PHYS, JV_FEATURES,
    enforce_feature_order
)


def _generate_composition(trial: optuna.Trial, a_site_pool: List[str], c_site_pool: List[str]) -> PerovskiteComposition:
    # A-site sampling from the provided pool
    a_site = []
    raw_vals_a = {}
    for name in a_site_pool:
        raw_vals_a[name] = trial.suggest_float(f"A_{name}_raw", 0.0, 1.0)

    total_a = sum(raw_vals_a.values())
    if total_a == 0: total_a = 1.0  # Avoid division by zero
    for name in a_site_pool:
        a_site.append(ElementFraction(name=Element(name), frequence=raw_vals_a[name] / total_a))

    # B-site: Hardcoded to Lead (Pb)
    b_site = [ElementFraction(name=Element("Pb"), frequence=1.0)]

    # C-site sampling from the provided halide pool (total must be 3.0)
    c_site = []
    raw_vals_c = {}
    for name in c_site_pool:
        raw_vals_c[name] = trial.suggest_float(f"C_{name}_raw", 0.0, 1.0)

    total_c_raw = sum(raw_vals_c.values())
    if total_c_raw == 0: total_c_raw = 1.0
    for name in c_site_pool:
        c_site.append(ElementFraction(name=Element(name), frequence=(raw_vals_c[name] / total_c_raw) * 3.0))

    return PerovskiteComposition(A_site=a_site, B_site=b_site, C_site=c_site)


def _composition_to_features(comp: PerovskiteComposition, is_inorganic: bool) -> Dict[str, Any]:
    from ml_prediction_web_service.services.preparation import _create_features_dict
    return _create_features_dict(comp, is_inorganic)


def search_optimal_band_gap(request: BandGapDiscoveryRequest, components: AppComponents) -> BandGapDiscoveryResponse:
    target = request.target_band_gap
    model = components.model_repository.get_band_gap_cat_model()
    bg_feature_list = MATERIAL_PHYS + COEF_FEATURES + CAT_SITES + ['dimension']
    cat_cols = CAT_SITES + ['dimension']

    a_site_pool = request.a_site_cations
    c_site_pool = request.c_site_anions

    if not a_site_pool or not c_site_pool:
        return BandGapDiscoveryResponse(
            composition_long_form="No elements selected", composition_short_form="N/A",
            predicted_band_gap=0, tolerance_factor=0, octahedral_factor=0,
            optimization_message="Error: You must provide A-site cations and C-site anions for optimization."
        )

    def objective(trial):
        comp = _generate_composition(trial, a_site_pool, c_site_pool)
        feat = _composition_to_features(comp, request.is_inorganic)
        tf = feat["tolerance_factor"]
        if tf < 0.80 or tf > 1.10: return 1e6  # Slightly broader range for experimental search

        df_ordered = enforce_feature_order(pd.DataFrame([feat]), bg_feature_list, cat_cols)
        pred = model.predict(df_ordered)[0]

        trial.set_user_attr("res", {"comp": comp, "bg": pred, "tf": tf, "of": feat["octahedral_factor"]})
        return abs(pred - target)

    study = optuna.create_study(direction="minimize", sampler=TPESampler(seed=42))
    study.optimize(objective, n_trials=request.max_trials)

    # Experimental search: continue up to 2000 trials
    ABS_MAX_TRIALS = 2000
    THRESHOLD = 0.01

    if study.best_value > THRESHOLD and request.max_trials < ABS_MAX_TRIALS:
        study.optimize(objective, n_trials=ABS_MAX_TRIALS - request.max_trials)

    if "res" not in study.best_trial.user_attrs:
        return BandGapDiscoveryResponse(
            composition_long_form="No stable composition found", composition_short_form="N/A",
            predicted_band_gap=0, tolerance_factor=0, octahedral_factor=0,
            optimization_message="Optimization failed to find any stable composition."
        )

    best = study.best_trial.user_attrs["res"]
    if study.best_value <= THRESHOLD:
        opt_msg = "User request is optimized and ready."
    else:
        opt_msg = f"Target {target} eV not fully reached after {len(study.trials)} trials. Best found: {best['bg']:.3f} eV."

    return BandGapDiscoveryResponse(
        composition_long_form=str(best["comp"]), composition_short_form=best["comp"].to_short_form(),
        predicted_band_gap=best["bg"], tolerance_factor=best["tf"], octahedral_factor=best["of"],
        optimization_message=opt_msg
    )


def search_optimal_solar_panel(request: SolarPanelDiscoveryRequest,
                               components: AppComponents) -> SolarPanelDiscoveryResponse:
    target_t80 = request.target_pce_t80
    t80_model = components.model_repository.get_pce_t80_cat_model()
    bg_model = components.model_repository.get_band_gap_cat_model()
    pce_model = components.model_repository.get_initial_pce_cat_model()

    all_cat = list(set(CAT_SITES + CAT_DEVICE))
    bg_feature_list = MATERIAL_PHYS + COEF_FEATURES + CAT_SITES + ['dimension']
    pce_feature_list = MATERIAL_PHYS + COEF_FEATURES + PROCESSING_PHYS + ['band_gap'] + all_cat
    t80_feature_list = MATERIAL_PHYS + COEF_FEATURES + PROCESSING_PHYS + STRESS_PHYS + JV_FEATURES + ['band_gap',
                                                                                                      'stress_proxy'] + all_cat

    a_site_pool = request.a_site_cations
    c_site_pool = request.c_site_anions

    if not a_site_pool or not c_site_pool or not request.architectures or not request.etl_stacks or not request.htl_stacks or not request.backcontact_stacks:
        return SolarPanelDiscoveryResponse(
            composition_long_form="Required selections missing", composition_short_form="N/A",
            cell_architecture="N/A", etl_stack_sequence="N/A", htl_stack_sequence="N/A",
            backcontact_stack_sequence="N/A",
            predicted_pce_t80=0, predicted_band_gap=0, tolerance_factor=0, octahedral_factor=0,
            optimization_message="Error: You must provide A-site, C-site, and all device stack selections (Architecture, ETL, HTL, Back Contact)."
        )

    def objective(trial):
        comp = _generate_composition(trial, a_site_pool, c_site_pool)
        feat = _composition_to_features(comp, request.is_inorganic)
        tf = feat["tolerance_factor"]
        if tf < 0.78 or tf > 1.12: return 1e6

        arch = trial.suggest_categorical("arch", request.architectures)
        etl = trial.suggest_categorical("etl", request.etl_stacks)
        htl = trial.suggest_categorical("htl", request.htl_stacks)
        bc = trial.suggest_categorical("bc", request.backcontact_stacks)

        # Annealing: fixed if provided, otherwise optimized
        ann_temp = request.annealing_temp if request.annealing_temp is not None else trial.suggest_float("ann_temp",
                                                                                                         70.0, 180.0)
        ann_time = request.annealing_time if request.annealing_time is not None else trial.suggest_float("ann_time",
                                                                                                         5.0, 60.0)

        # 1. Band Gap
        bg_df = enforce_feature_order(pd.DataFrame([feat]), bg_feature_list, CAT_SITES + ['dimension'])
        bg_pred = bg_model.predict(bg_df)[0]

        # 2. Initial PCE
        pce_feat = feat.copy()
        pce_feat.update({
            "cell_architecture": arch, "etl_stack_sequence": etl, "htl_stack_sequence": htl,
            "backcontact_stack_sequence": bc,
            "perovskite_annealing_temp": ann_temp, "perovskite_annealing_time": ann_time, "band_gap": bg_pred
        })
        pce_df = enforce_feature_order(pd.DataFrame([pce_feat]), pce_feature_list, all_cat)
        pce_pred = pce_model.predict(pce_df)[0]

        # 3. T80
        t80_feat = pce_feat.copy()
        t80_feat.update({
            "stability_protocol": "ISOS-L-1", "stability_light_intensity": 1.0, "acc_temp": 25.0, "acc_humidity": 50.0,
            "jv_default_pce": pce_pred, "jv_default_voc": 1.1, "jv_default_jsc": 22.0, "jv_default_ff": 0.75,
            "stress_proxy": pce_pred * tf
        })
        t80_df = enforce_feature_order(pd.DataFrame([t80_feat]), t80_feature_list, all_cat)
        t80_pred_log = t80_model.predict(t80_df)[0]
        t80_pred = np.expm1(t80_pred_log)

        res = {
            "comp": comp, "bg": bg_pred, "pce": pce_pred, "t80": t80_pred, "tf": tf, "of": feat["octahedral_factor"],
            "arch": arch, "etl": etl, "htl": htl, "bc": bc, "ann_temp": ann_temp, "ann_time": ann_time
        }
        trial.set_user_attr("res", res)
        return abs(np.log1p(t80_pred) - np.log1p(target_t80))

    study = optuna.create_study(direction="minimize", sampler=TPESampler(seed=42))
    study.optimize(objective, n_trials=request.max_trials)

    # Experimental search: continue up to 2000 trials
    ABS_MAX_TRIALS = 2000
    LOG_THRESHOLD = 0.03

    if study.best_value > LOG_THRESHOLD and request.max_trials < ABS_MAX_TRIALS:
        study.optimize(objective, n_trials=ABS_MAX_TRIALS - request.max_trials)

    if "res" not in study.best_trial.user_attrs:
        return SolarPanelDiscoveryResponse(
            composition_long_form="No stable configuration found", composition_short_form="N/A",
            cell_architecture="N/A", etl_stack_sequence="N/A", htl_stack_sequence="N/A",
            backcontact_stack_sequence="N/A",
            predicted_pce_t80=0, predicted_band_gap=0, tolerance_factor=0, octahedral_factor=0,
            optimization_message="Optimization failed to find any stable device configuration."
        )

    best = study.best_trial.user_attrs["res"]
    if study.best_value <= LOG_THRESHOLD:
        opt_msg = "User request is optimized and ready."
    else:
        opt_msg = f"Target T80 of {target_t80}h not fully reached after {len(study.trials)} trials. Best found: {best['t80']:.1f}h."

    return SolarPanelDiscoveryResponse(
        composition_long_form=str(best["comp"]),
        composition_short_form=best["comp"].to_short_form(),
        cell_architecture=best["arch"],
        etl_stack_sequence=best["etl"],
        htl_stack_sequence=best["htl"],
        backcontact_stack_sequence=best["bc"],
        predicted_pce_t80=best["t80"],
        predicted_band_gap=best["bg"],
        tolerance_factor=best["tf"],
        octahedral_factor=best["of"],
        optimization_message=opt_msg
    )
