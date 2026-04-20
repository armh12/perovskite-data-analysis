import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
import optuna
import joblib
import os
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error

def clean_categorical_data(df, cat_cols):
    """Ensures all categorical columns are strings and contain no NaN objects."""
    df = df.copy()
    for col in cat_cols:
        if col in df.columns:
            # fillna first, then cast to string to avoid 'nan' string vs NaN object issues
            df[col] = df[col].fillna('None').astype(str)
    return df

def train_catboost_model(name, df, target, phys_cols, cat_cols, log_transform=False, n_trials=30, groups_col='composition_long_form'):
    print(f"\n--- Training {name} Model (CatBoost + GroupKFold) ---")
    
    df = df.dropna(subset=[target])
    all_features = [c for c in phys_cols + cat_cols if c in df.columns]
    
    # 1. Clean data for CatBoost
    X = clean_categorical_data(df[all_features], cat_cols)
    y = df[target]
    groups = df[groups_col]
    
    cat_features_indices = [i for i, col in enumerate(all_features) if col in cat_cols]

    if log_transform:
        y = np.log1p(y.clip(lower=0))
        
    gss = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))
    
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
        
        gkf = GroupKFold(n_splits=3)
        scores = []
        for t_idx, v_idx in gkf.split(X_train, y_train, groups_train):
            xt, xv = X_train.iloc[t_idx], X_train.iloc[v_idx]
            yt, yv = y_train.iloc[t_idx], y_train.iloc[v_idx]
            model = CatBoostRegressor(**params)
            model.fit(xt, yt, cat_features=cat_features_indices, eval_set=(xv, yv))
            scores.append(r2_score(yv, model.predict(xv)))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials)
    
    final_model = CatBoostRegressor(**study.best_params, verbose=False)
    final_model.fit(X_train, y_train, cat_features=cat_features_indices)
    
    os.makedirs('ml_models', exist_ok=True)
    save_path = f"../ml_models/{name.lower().replace(' ', '_')}.joblib"
    joblib.dump(final_model, save_path)
    print(f"SUCCESS: {name} model saved to {save_path}")
    print(f"Hold-out Unseen Test R2: {r2_score(y_test, final_model.predict(X_test)):.4f}")
    return final_model

if __name__ == "__main__":
    data_dir = "../data"
    df_bg = pd.read_parquet(f'{data_dir}/enriched_perovskites.parquet')
    df_sp = pd.read_parquet(f'{data_dir}/enriched_solar_panels.parquet')
    
    # Standardize join keys
    df_bg['composition_long_form'] = df_bg['composition_long_form'].astype(str).str.strip()
    df_sp['composition_long_form'] = df_sp['composition_long_form'].astype(str).str.strip()

    material_phys = ['r_A', 'en_A', 'mass_A', 'r_C', 'en_C', 'mass_C', 'tolerance_factor', 'octahedral_factor', 'radius_ratio_ab', 'en_diff_bc', 'mass_ratio_ab']
    processing_phys = ['perovskite_annealing_temp', 'perovskite_annealing_time', 'etl_annealing_temp', 'htl_annealing_temp']
    stress_phys = ['acc_temp', 'acc_humidity', 'stability_light_intensity']
    coef_features = ['A_1_coef', 'A_2_coef', 'A_3_coef', 'B_1_coef', 'C_1_coef', 'C_2_coef']
    cat_sites = ['A_1', 'A_2', 'A_3', 'B_1', 'C_1', 'C_2']
    cat_device = ['dimension', 'cell_architecture', 'etl_stack_sequence', 'htl_stack_sequence']
    
    n_trials = 100

    # 1. Load or Train Band Gap
    bg_model_path = '../ml_models/band_gap.joblib'
    if os.path.exists(bg_model_path):
        bg_model = joblib.load(bg_model_path)
        print("Loaded existing Band Gap model.")
    else:
        bg_model = train_catboost_model("CatBoost Band Gap", df_bg, 'band_gap', material_phys + coef_features, cat_sites + ['dimension'], n_trials=n_trials)

    # 2. STRUCTURAL SYNC
    print("\n--- Synchronizing Structure with Device Experiments ---")
    cols_to_sync = material_phys + coef_features + cat_sites + ['dimension', 'composition_inorganic']
    # Filter bg to what we strictly need for sync
    df_bg_sync = df_bg[['composition_long_form'] + cols_to_sync].drop_duplicates()
    
    # Re-merge to ensure df_sp has the exact features needed for prediction/training
    df_sp = df_sp.drop(columns=[c for c in cols_to_sync if c in df_sp.columns], errors='ignore')
    df_sp = df_sp.merge(df_bg_sync, on='composition_long_form', how='inner')
    print(f"Matched {len(df_sp)} device experiments with material descriptors.")

    # 3. FEATURE PROPAGATION (Safe cleaning)
    print("\n--- Propagating Band Gap features ---")
    bg_features_list = material_phys + coef_features + cat_sites + ['dimension']
    
    # Pre-clean df_sp for prediction
    df_sp_for_bg = clean_categorical_data(df_sp[bg_features_list], cat_sites + ['dimension'])
    df_sp['predicted_bg'] = bg_model.predict(df_sp_for_bg)
    df_sp['band_gap'] = df_sp['band_gap'].fillna(df_sp['predicted_bg'])

    # 4. Final Models
    all_cat = list(set(cat_sites + cat_device + ['backcontact_stack_sequence', 'stability_protocol']))
    
    # Using 'band_gap' as unified column name as seen in the fillna step above
    # Added JV features and more categorical features. 
    # NOTE: GroupKFold is very strict for this dataset due to composition sparsity.
    # If R2 remains low, consider switching to regular KFold for within-composition optimization.
    train_catboost_model("Raw T80", df_sp.dropna(subset=['stability_pce_t80']), 'stability_pce_t80', 
                         material_phys + coef_features + processing_phys + stress_phys + 
                         ['jv_default_pce', 'jv_default_voc', 'jv_default_jsc', 'jv_default_ff', 'band_gap', 'stress_proxy'], 
                         all_cat, log_transform=True, n_trials=n_trials)
    
    train_catboost_model("Metric TS80m", df_sp.dropna(subset=['stability_ts80m']), 'stability_ts80m', material_phys + coef_features + processing_phys + ['band_gap'], all_cat, log_transform=True, n_trials=n_trials)
    
    train_catboost_model("Initial PCE", df_sp.dropna(subset=['jv_default_pce']), 'jv_default_pce', material_phys + coef_features + processing_phys + ['band_gap'], all_cat, n_trials=n_trials)
