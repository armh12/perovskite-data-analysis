import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
import optuna
import joblib
import os
from sklearn.model_selection import GroupKFold, KFold, GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error

def clean_categorical_data(df, cat_cols):
    """Ensures all categorical columns are strings and contain no NaN objects."""
    df = df.copy()
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna('None').astype(str)
    return df

def train_catboost_model(name, df, target, phys_cols, cat_cols, log_transform=False, n_trials=30, groups_col='composition_long_form', use_group_kfold=True):
    print(f"\n--- Training {name} Model ({'GroupKFold' if use_group_kfold else 'KFold'}) ---")
    
    df = df.dropna(subset=[target])
    all_features = [c for c in phys_cols + cat_cols if c in df.columns]
    
    X = clean_categorical_data(df[all_features], cat_cols)
    y = df[target]
    groups = df[groups_col]
    
    cat_features_indices = [i for i, col in enumerate(all_features) if col in cat_cols]

    if log_transform:
        y = np.log1p(y.clip(lower=0))
        
    if use_group_kfold:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups))
    else:
        from sklearn.model_selection import train_test_split
        train_idx, test_idx = train_test_split(np.arange(len(X)), test_size=0.15, random_state=42)
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train = groups.iloc[train_idx]

    def objective(trial):
        params = {
            'iterations': trial.suggest_int('iterations', 500, 2000),
            'depth': trial.suggest_int('depth', 4, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1e-2, 10.0, log=True),
            'random_strength': trial.suggest_float('random_strength', 1e-2, 10.0, log=True),
            'bagging_temperature': trial.suggest_float('bagging_temperature', 0.0, 1.0),
            'od_type': 'Iter',
            'od_wait': 50,
            'verbose': False,
            'random_state': 42
        }
        
        cv = GroupKFold(n_splits=3) if use_group_kfold else KFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        cv_split = cv.split(X_train, y_train, groups_train) if use_group_kfold else cv.split(X_train, y_train)
        
        for t_idx, v_idx in cv_split:
            xt, xv = X_train.iloc[t_idx], X_train.iloc[v_idx]
            yt, yv = y_train.iloc[t_idx], y_train.iloc[v_idx]
            model = CatBoostRegressor(**params)
            model.fit(xt, yt, cat_features=cat_features_indices, eval_set=(xv, yv))
            scores.append(r2_score(yv, model.predict(xv)))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials)
    
    # 1. Final Mean Model
    final_params = study.best_params.copy()
    final_model = CatBoostRegressor(**final_params, verbose=False)
    final_model.fit(X_train, y_train, cat_features=cat_features_indices)
    
    os.makedirs('../ml_models', exist_ok=True)
    base_filename = name.lower().replace(' ', '_')
    joblib.dump(final_model, f"../ml_models/{base_filename}.joblib")
    
    # 2. Train Quantile Models for Uncertainty
    print(f"--- Training Quantile Models for {name} ---")
    for alpha in [0.05, 0.95]:
        q_params = final_params.copy()
        q_params['loss_function'] = f'Quantile:alpha={alpha}'
        # Quantile regression doesn't use R2 for early stopping, but we use iterations from best mean model
        q_model = CatBoostRegressor(**q_params, verbose=False)
        q_model.fit(X_train, y_train, cat_features=cat_features_indices)
        suffix = "q05" if alpha == 0.05 else "q95"
        joblib.dump(q_model, f"../ml_models/{base_filename}_{suffix}.joblib")

    print(f"SUCCESS: {name} models saved.")
    print(f"Hold-out Test R2: {r2_score(y_test, final_model.predict(X_test)):.4f}")
    return final_model

if __name__ == "__main__":
    data_dir = "../data"
    df_bg = pd.read_parquet(f'{data_dir}/enriched_perovskites.parquet')
    df_sp = pd.read_parquet(f'{data_dir}/enriched_solar_panels.parquet')
    
    df_bg['composition_long_form'] = df_bg['composition_long_form'].astype(str).str.strip()
    df_sp['composition_long_form'] = df_sp['composition_long_form'].astype(str).str.strip()

    material_phys = ['r_A', 'en_A', 'mass_A', 'r_C', 'en_C', 'mass_C', 'tolerance_factor', 'octahedral_factor', 'radius_ratio_ab', 'en_diff_bc', 'mass_ratio_ab']
    processing_phys = ['perovskite_annealing_temp', 'perovskite_annealing_time']
    stress_phys = ['acc_temp', 'acc_humidity', 'stability_light_intensity']
    coef_features = ['A_1_coef', 'A_2_coef', 'A_3_coef', 'B_1_coef', 'C_1_coef', 'C_2_coef']
    cat_sites = ['A_1', 'A_2', 'A_3', 'B_1', 'C_1', 'C_2']
    cat_device = ['dimension', 'cell_architecture', 'etl_stack_sequence', 'htl_stack_sequence', 'backcontact_stack_sequence', 'stability_protocol']
    jv_features = ['jv_default_pce', 'jv_default_voc', 'jv_default_jsc', 'jv_default_ff']
    
    n_trials = 150

    # 1. Band Gap
    bg_model = train_catboost_model("Band Gap", df_bg, 'band_gap', material_phys + coef_features, cat_sites + ['dimension'], n_trials=n_trials, use_group_kfold=True)

    # 2. JIT MERGE
    print("\n--- Synchronizing Structure with Device Experiments ---")
    cols_to_sync = material_phys + coef_features + cat_sites + ['dimension', 'composition_inorganic', 'band_gap']
    df_bg_sync = df_bg[['composition_long_form'] + cols_to_sync].drop_duplicates()
    df_sp = df_sp.merge(df_bg_sync, on='composition_long_form', how='inner')

    # 3. FEATURE PROPAGATION
    bg_features_list = material_phys + coef_features + cat_sites + ['dimension']
    df_sp_for_bg = clean_categorical_data(df_sp[bg_features_list], cat_sites + ['dimension'])
    df_sp['predicted_bg'] = bg_model.predict(df_sp_for_bg)
    df_sp['band_gap'] = df_sp['band_gap'].fillna(df_sp['predicted_bg'])
    df_sp['stress_proxy'] = df_sp['jv_default_pce'] * df_sp['tolerance_factor']

    # 4. Final Models
    all_cat = list(set(cat_sites + cat_device))

    train_catboost_model("Raw T80", df_sp.dropna(subset=['stability_pce_t80']), 'stability_pce_t80', 
                         material_phys + coef_features + processing_phys + stress_phys + jv_features + ['band_gap', 'stress_proxy'], 
                         all_cat, log_transform=True, n_trials=n_trials, use_group_kfold=False)
    
    train_catboost_model("Metric TS80m", df_sp.dropna(subset=['stability_ts80m']), 'stability_ts80m', 
                         material_phys + coef_features + processing_phys + stress_phys + jv_features + ['band_gap', 'stress_proxy'], 
                         all_cat, log_transform=True, n_trials=n_trials, use_group_kfold=False)
    
    train_catboost_model("Initial PCE", df_sp.dropna(subset=['jv_default_pce']), 'jv_default_pce', 
                         material_phys + coef_features + processing_phys + ['band_gap'], 
                         all_cat, n_trials=n_trials, use_group_kfold=True)
