import enum


@enum.unique
class SavedModelName(enum.Enum):
    # Band Gap models (CatBoost)
    BAND_GAP_CAT = "band_gap.joblib"
    BAND_GAP_CAT_LOW = "band_gap_q05.joblib"
    BAND_GAP_CAT_HIGH = "band_gap_q95.joblib"
    
    # Stability models (CatBoost)
    PCE_T80_CAT = "raw_t80.joblib"
    PCE_T80_CAT_LOW = "raw_t80_q05.joblib"
    PCE_T80_CAT_HIGH = "raw_t80_q95.joblib"
    
    TS80M_CAT = "metric_ts80m.joblib"
    TS80M_CAT_LOW = "metric_ts80m_q05.joblib"
    TS80M_CAT_HIGH = "metric_ts80m_q95.joblib"
    
    # Efficiency model (CatBoost)
    INITIAL_PCE_CAT = "initial_pce.joblib"
    INITIAL_PCE_CAT_LOW = "initial_pce_q05.joblib"
    INITIAL_PCE_CAT_HIGH = "initial_pce_q95.joblib"

    # Legacy / Quantile (Keep for compatibility if needed by other parts)
    BAND_GAP_XGB = "xgboost_band_gap.joblib"
    BAND_GAP_LOW = "xgboost_band_gap_q05.joblib"
    BAND_GAP_HIGH = "xgboost_band_gap_q95.joblib"
    
    PCE_T80_XGB = "pce_t80_model.joblib"
    PCE_T80_LOW = "pce_t80_model_q05.joblib"
    PCE_T80_HIGH = "pce_t80_model_q95.joblib"
    
    PCE_JV_XGB = "pce_jv_model.joblib"
